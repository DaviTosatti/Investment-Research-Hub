"""Bounded, synchronous statement reconciliation. Original files and revisions are immutable."""

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal

from hub_finance.ledger import METHOD_VERSION, LedgerError, apply_event, decimal_string, event_gross
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, defer

from hub_api.errors import AppError
from hub_api.import_parser import ParseError, parse_table
from hub_api.import_schemas import PreviewCreate
from hub_api.models import (
    AuditEvent,
    DataSource,
    ImportBatch,
    ImportPreview,
    ImportReceipt,
    Instrument,
    Listing,
    OriginalFile,
    Transaction,
    User,
    identifier,
    now,
)
from hub_api.portfolio_service import MAX_EVENTS, event_rows, replay
from hub_api.schemas import TransactionCreate, today
from hub_api.transaction_service import append_event, as_event, lock_portfolio

AMOUNTS = ("quantity", "unit_price", "gross_amount", "fees", "taxes")
EVENT_NAMES = {
    "aporte": "deposit",
    "retirada": "withdrawal",
    "compra": "buy",
    "venda": "sell",
    "dividendo": "dividend",
    "taxa": "fee",
    "imposto": "tax",
    "desdobramento": "split",
}


def fingerprint(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def audit_import(db: Session, actor: User, action: str, entity: str, entity_id: str):
    db.add(AuditEvent(actor_id=actor.id, action=action, entity_type=entity, entity_id=entity_id))


def get_batch(db: Session, batch_id: str, *, lock: bool = False) -> ImportBatch:
    query = select(ImportBatch).where(ImportBatch.id == batch_id)
    batch = db.scalar(query.with_for_update() if lock else query)
    if not batch:
        raise AppError(404, "NOT_FOUND", "Importação não encontrada.")
    return batch


def latest_preview(
    db: Session, batch_id: str, *, summary_only: bool = False
) -> ImportPreview | None:
    query = select(ImportPreview)
    if summary_only:
        query = query.options(defer(ImportPreview.rows), defer(ImportPreview.config))
    return db.scalar(
        query.where(ImportPreview.import_id == batch_id)
        .order_by(ImportPreview.revision.desc())
        .limit(1)
    )


def receipt_for(db: Session, batch_id: str) -> ImportReceipt | None:
    return db.scalar(select(ImportReceipt).where(ImportReceipt.import_id == batch_id))


def upload(
    db: Session,
    actor: User,
    portfolio_id: str,
    source_id: str,
    filename: str,
    content: bytes,
    options: dict,
) -> tuple[ImportBatch, bool]:
    lock_portfolio(db, portfolio_id)
    if not db.get(DataSource, source_id):
        raise AppError(404, "NOT_FOUND", "Fonte não encontrada.")
    if not filename or len(filename) > 180 or re.search(r"[\\/\x00-\x1f\x7f]", filename):
        raise AppError(422, "INVALID_FILE", "Use somente o nome do arquivo, sem caminho.")
    try:
        table = parse_table(content, filename, **options)
    except ParseError as exc:
        raise AppError(422, "INVALID_FILE", str(exc)) from exc
    sha256 = hashlib.sha256(content).hexdigest()
    # PostgreSQL handles identical uploads from different portfolios atomically.
    original_id = db.scalar(
        insert(OriginalFile)
        .values(
            id=identifier(),
            sha256=sha256,
            content=content,
            size=len(content),
            created_by=actor.id,
            created_at=now(),
        )
        .on_conflict_do_nothing(index_elements=["sha256"])
        .returning(OriginalFile.id)
    )
    if original_id is None:
        original_id = db.scalar(select(OriginalFile.id).where(OriginalFile.sha256 == sha256))
    parse_key = fingerprint({**options, "extension": filename.rsplit(".", 1)[-1].lower()})
    existing = db.scalar(
        select(ImportBatch).where(
            ImportBatch.portfolio_id == portfolio_id,
            ImportBatch.source_id == source_id,
            ImportBatch.original_id == original_id,
            ImportBatch.parse_key == parse_key,
        )
    )
    if existing:
        return existing, False
    batch = ImportBatch(
        portfolio_id=portfolio_id,
        source_id=source_id,
        original_id=original_id,
        filename=filename,
        parse_key=parse_key,
        parse_options=options,
        table=asdict(table),
        created_by=actor.id,
    )
    db.add(batch)
    db.flush()
    audit_import(db, actor, "upload", "import", batch.id)
    return batch, True


def economic_key(value: TransactionCreate | Transaction, *, candidate: bool = False) -> str:
    """Possible economic equality is NOT identity; without external IDs require review."""
    gross = (
        event_gross(as_event(value)) if isinstance(value, TransactionCreate) else value.gross_amount
    )
    if (
        isinstance(value, TransactionCreate)
        and value.event_type in {"buy", "sell"}
        and value.gross_amount not in (Decimal("0"), gross)
    ):
        raise LedgerError("Valor bruto diverge de quantidade vezes preço.")
    values = {
        "instrument": str(value.instrument_id) if value.instrument_id else None,
        "event": value.event_type,
        "trade": value.trade_date.isoformat(),
        "settlement": value.settlement_date.isoformat(),
        "quantity": format(value.quantity.normalize(), "f"),
        "price": format(value.unit_price.normalize(), "f"),
        "gross": format(gross.normalize(), "f"),
        "fees": format(value.fees.normalize(), "f"),
        "taxes": format(value.taxes.normalize(), "f"),
    }
    if candidate:
        # Optional/defaulted settlement and charges cannot establish distinct executions.
        for field in ("settlement", "fees", "taxes"):
            values.pop(field)
    return fingerprint(values)


def normalized_payload(db: Session, batch: ImportBatch, config: PreviewCreate, row: dict):
    values = {field: row["values"].get(column) for field, column in config.mapping.items()}
    edit = next((e for e in config.edits if e.row_number == row["number"]), None)
    if edit:
        values.update(edit.values)
    if row["errors"]:
        raise ValueError("; ".join(row["errors"]))
    if config.mapping.get("external_id") in row.get("numeric_columns", []) and not (
        edit and "external_id" in edit.values
    ):
        raw_id = values.get("external_id")
        if raw_id:
            numeric_id = Decimal(raw_id)
            if (
                not numeric_id.is_finite()
                or numeric_id < 0
                or numeric_id.adjusted() >= 160
                or abs(numeric_id.as_tuple().exponent) > 160
                or numeric_id != numeric_id.to_integral_value()
            ):
                raise ValueError(
                    "Referência externa numérica deve ser um inteiro; confira sua identificação textual."
                )
            values["external_id"] = format(numeric_id.to_integral_value(), "f") if numeric_id else "0"
    event_type = (values.get("event_type") or "").strip()
    event_type = config.event_values.get(
        event_type, EVENT_NAMES.get(event_type.lower(), event_type.lower())
    )
    trade_date = values.get("trade_date")
    if not trade_date:
        raise ValueError("Data da operação ausente.")
    fmt = "%Y-%m-%d" if config.date_format == "YYYY-MM-DD" else "%d/%m/%Y"
    dates = {}
    for field in ("trade_date", "settlement_date"):
        raw = values.get(field)
        if raw:
            # XLSX date cells are canonical ISO strings; text columns follow chosen format.
            selected_fmt = "%Y-%m-%d" if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw) else fmt
            try:
                dates[field] = datetime.strptime(raw, selected_fmt).date()
            except ValueError as exc:
                raise ValueError(f"{field}: data incompatível com o formato selecionado.") from exc
        elif field in values:
            raise ValueError(
                f"{field}: célula vazia; retire o mapeamento para usar a data da operação."
            )
    currency = values.get("currency", "BRL")
    if currency != "BRL":
        raise ValueError("Moeda ausente ou não suportada. Este importador trabalha em BRL.")
    numbers = {}
    required = (
        {"quantity", "unit_price"}
        if event_type in {"buy", "sell"}
        else ({"quantity"} if event_type == "split" else {"gross_amount"})
    )
    for field in AMOUNTS:
        raw = values.get(field)
        if raw is None or raw == "":
            if field in required or field in values:
                raise ValueError(f"{field}: valor ausente; nulo não é zero.")
            numbers[field] = "0"
            continue
        # Numeric XLSX cells use XML point notation independently of presentation.
        # Text/CSV amounts use an explicit separator and forbid ambiguous grouping.
        separator = config.decimal_separator
        numeric_cell = config.mapping.get(field) in row.get("numeric_columns", [])
        if edit and field in edit.values:
            numeric_cell = False
        if numeric_cell and re.fullmatch(r"\d+(\.\d+)?([Ee][+-]?\d+)?", raw):
            number = Decimal(raw)
            if number.adjusted() >= 10 or abs(number.as_tuple().exponent) > 50:
                raise ValueError(f"{field}: valor ou escala excede os limites do importador.")
            numbers[field] = format(number, "f")
        else:
            if not re.fullmatch(r"\d+(?:" + re.escape(separator) + r"\d+)?", raw):
                raise ValueError(
                    f"{field}: use o separador decimal escolhido, sem milhares ou símbolos."
                )
            numbers[field] = raw.replace(",", ".")
    instrument_id = values.get("instrument_id")
    ticker = values.get("ticker")
    exchange = (values.get("exchange") or config.exchange).upper()
    if ticker:
        listing = db.scalar(
            select(Listing).where(Listing.ticker == ticker.upper(), Listing.exchange == exchange)
        )
        if not listing:
            raise ValueError("Ticker/mercado não cadastrado; cadastre o ativo ou corrija a linha.")
        if instrument_id and instrument_id != listing.instrument_id:
            raise ValueError("O ID do instrumento diverge do ticker/mercado.")
        if (listing.valid_from and dates["trade_date"] < listing.valid_from) or (
            listing.valid_to and dates["trade_date"] > listing.valid_to
        ):
            raise ValueError("A operação está fora da vigência da listagem cadastrada.")
        instrument_id = listing.instrument_id
    if instrument_id and not db.get(Instrument, instrument_id):
        raise ValueError("ID do instrumento não cadastrado.")
    if (
        event_type in {"buy", "sell"}
        and "gross_amount" in values
        and Decimal(numbers["gross_amount"]) <= 0
    ):
        raise ValueError(
            "Valor bruto informado deve ser positivo e conferir com quantidade vezes preço."
        )
    return TransactionCreate(
        portfolio_id=batch.portfolio_id,
        instrument_id=instrument_id,
        event_type=event_type,
        **numbers,
        **dates,
        source="import:" + batch.source_id,
        external_id=values.get("external_id") or None,
        notes=values.get("notes") or None,
        idempotency_key=f"import:{batch.id}:{row['number']}",
    )


def build_preview(
    db: Session, batch: ImportBatch, config: PreviewCreate, actor: User
) -> ImportPreview:
    if receipt_for(db, batch.id):
        raise AppError(409, "IMPORT_COMMITTED", "Esta importação já foi confirmada.")
    lock_portfolio(db, batch.portfolio_id)
    if not set(config.mapping.values()).issubset(batch.table["headers"]):
        raise AppError(422, "INVALID_MAPPING", "O mapeamento contém colunas ausentes no arquivo.")
    row_numbers = {r["number"] for r in batch.table["rows"]}
    if any(e.row_number not in row_numbers for e in [*config.edits, *config.decisions]):
        raise AppError(
            422, "INVALID_ROW", "Alteração ou decisão refere-se a uma linha inexistente."
        )
    events = event_rows(db, [batch.portfolio_id], today())
    state = replay(events)
    before = decimal_string(state.cash)
    last_date = events[-1].trade_date if events else None
    candidates = defaultdict(list)
    external = {}
    for event in events:
        key = economic_key(event)
        reference = {
            "transaction_id": event.id,
            "row_number": None,
            "key": key,
            "source": event.source,
            "external_id": event.external_id,
        }
        candidates[economic_key(event, candidate=True)].append(reference)
        if event.source == "import:" + batch.source_id and event.external_id:
            external[event.external_id] = reference
    decisions = {d.row_number: d for d in config.decisions}
    results, parsed = [], []
    for row in batch.table["rows"]:
        decision = decisions.get(row["number"])
        item = {
            "row_number": row["number"],
            "raw": row["values"],
            "normalized": None,
            "status": "quarantined",
            "errors": [],
            "candidates": [],
            "candidate_count": 0,
            "calculated_gross_amount": None,
            "decision": decision.model_dump() if decision else None,
            "transaction_id": None,
            "duplicate_of_row": None,
        }
        results.append(item)
        if decision and decision.action == "skip":
            item["status"] = "excluded"
            item["errors"] = row["errors"]
            continue
        try:
            payload = normalized_payload(db, batch, config, row)
            item["normalized"] = payload.model_dump(mode="json")
            item["calculated_gross_amount"] = decimal_string(event_gross(as_event(payload)))
            parsed.append((payload, item))
        except ValidationError as exc:
            fields = ", ".join(".".join(map(str, e["loc"])) for e in exc.errors())
            item["errors"] = [f"Confira {fields}: valores, limites e datas da operação."]
        except (ValueError, LedgerError) as exc:
            item["errors"] = [str(exc)]
    # Preserve statement order inside a day; order dates before applying the canonical engine.
    parsed.sort(key=lambda pair: (pair[0].trade_date, pair[1]["row_number"]))
    ready = 0
    for payload, item in parsed:
        try:
            key = economic_key(payload)
            duplicate = external.get(payload.external_id) if payload.external_id else None
            if duplicate:
                if duplicate["key"] != key:
                    item["errors"] = [
                        "Referência externa já usada com valores diferentes; revise a origem."
                    ]
                    continue
                item.update(
                    status="duplicate",
                    transaction_id=duplicate["transaction_id"],
                    duplicate_of_row=duplicate["row_number"],
                )
                continue
            possible = candidates[economic_key(payload, candidate=True)]
            item["candidate_count"] = len(possible)
            item["candidates"] = [
                {k: c[k] for k in ("transaction_id", "row_number")} for c in possible[:20]
            ]
            decision = decisions.get(item["row_number"])
            # Distinct provider IDs establish separate executions, including equal-sized trades.
            ambiguous = any(
                not (payload.external_id and c["external_id"] and c["source"] == payload.source)
                for c in possible
            )
            if ambiguous and (not decision or decision.action != "create"):
                item["status"] = "needs_review"
                item["errors"] = [
                    "Operação semelhante encontrada. Exclua a linha ou justifique uma nova operação."
                ]
                continue
            if last_date and payload.trade_date < last_date:
                raise ValueError(
                    "Data anterior ao histórico existente. Retificação de eventos confirmados ainda pendente."
                )
            if len(events) + ready >= MAX_EVENTS:
                raise ValueError("Limite de 20 mil eventos por carteira atingido.")
            apply_event(state, as_event(payload))
            item["status"] = "ready"
            ready += 1
            last_date = payload.trade_date
            reference = {
                "transaction_id": None,
                "row_number": item["row_number"],
                "key": key,
                "source": payload.source,
                "external_id": payload.external_id,
            }
            candidates[economic_key(payload, candidate=True)].append(reference)
            if payload.external_id:
                external[payload.external_id] = reference
        except (ValueError, LedgerError) as exc:
            item["errors"] = [str(exc)]
    counts = Counter(item["status"] for item in results)
    previous = latest_preview(db, batch.id)
    dates = [p.trade_date.isoformat() for p, _ in parsed]
    preview = ImportPreview(
        import_id=batch.id,
        revision=previous.revision + 1 if previous else 1,
        ledger_version=fingerprint([e.id for e in events]),
        config=config.model_dump(mode="json"),
        rows=results,
        summary={
            **{
                status: counts[status]
                for status in ("ready", "duplicate", "needs_review", "quarantined", "excluded")
            },
            "can_commit": not counts["quarantined"]
            and not counts["needs_review"]
            and bool(results),
            "cash_before": before,
            "cash_after": decimal_string(state.cash),
            "currency": "BRL",
            "quantity_unit": "units_or_split_factor",
            "amount_unit": "BRL",
            "period_start": min(dates) if dates else None,
            "period_end": max(dates) if dates else None,
            "method_version": METHOD_VERSION,
        },
        created_by=actor.id,
    )
    db.add(preview)
    db.flush()
    audit_import(db, actor, "preview", "import_snapshot", preview.id)
    return preview


def confirm(
    db: Session, batch: ImportBatch, preview_id: str, actor: User
) -> tuple[ImportReceipt, bool]:
    lock_portfolio(db, batch.portfolio_id)
    receipt = receipt_for(db, batch.id)
    if receipt:
        if receipt.preview_id != preview_id:
            raise AppError(409, "IMPORT_COMMITTED", "Uma outra prévia já foi confirmada.")
        return receipt, False
    preview = latest_preview(db, batch.id)
    if not preview or preview.id != preview_id:
        raise AppError(409, "PREVIEW_CHANGED", "Selecione a revisão mais recente da prévia.")
    if not preview.summary["can_commit"]:
        raise AppError(
            422,
            "UNRESOLVED_ROWS",
            "Corrija ou exclua explicitamente as linhas pendentes antes de confirmar.",
        )
    events = event_rows(db, [batch.portfolio_id], today())
    if (
        fingerprint([e.id for e in events]) != preview.ledger_version
        or preview.summary["method_version"] != METHOD_VERSION
    ):
        raise AppError(
            409, "STALE_PREVIEW", "O histórico mudou. Gere uma nova prévia antes de confirmar."
        )
    state = replay(events)
    portfolio = lock_portfolio(db, batch.portfolio_id)
    ids, results = {}, []
    ready = sorted(
        (r for r in preview.rows if r["status"] == "ready"),
        key=lambda r: (r["normalized"]["trade_date"], r["row_number"]),
    )
    for item in ready:
        payload = TransactionCreate.model_validate(item["normalized"])
        row = append_event(db, payload, actor, portfolio, state)
        ids[item["row_number"]] = row.id
    for item in preview.rows:
        transaction_id = ids.get(item["row_number"], item["transaction_id"])
        if item["duplicate_of_row"] is not None:
            transaction_id = ids[item["duplicate_of_row"]]
        results.append(
            {
                "row_number": item["row_number"],
                "status": item["status"],
                "transaction_id": transaction_id,
            }
        )
    receipt = ImportReceipt(
        import_id=batch.id, preview_id=preview.id, results=results, created_by=actor.id
    )
    db.add(receipt)
    db.flush()
    audit_import(db, actor, "confirm", "import", batch.id)
    return receipt, True
