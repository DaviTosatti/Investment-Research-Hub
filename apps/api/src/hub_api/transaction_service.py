"""One transactional write path for manual events and confirmed statement imports."""

import hashlib
import json

from hub_finance.ledger import Event, LedgerState, apply_event, event_gross
from sqlalchemy import select
from sqlalchemy.orm import Session

from hub_api.errors import AppError
from hub_api.models import AuditEvent, Instrument, JournalEntry, Portfolio, Transaction, User
from hub_api.portfolio_service import event_rows, replay
from hub_api.schemas import TransactionCreate, today


def canonical_hash(payload: TransactionCreate) -> str:
    values = payload.model_dump(mode="json", exclude={"idempotency_key"})
    for key in ("quantity", "unit_price", "gross_amount", "fees", "taxes"):
        values[key] = format(getattr(payload, key).normalize(), "f")
    return hashlib.sha256(
        json.dumps(values, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def as_event(payload: TransactionCreate) -> Event:
    return Event(
        payload.event_type,
        payload.trade_date,
        str(payload.instrument_id) if payload.instrument_id else None,
        payload.quantity,
        payload.unit_price,
        payload.gross_amount,
        payload.fees,
        payload.taxes,
    )


def lock_portfolio(db: Session, portfolio_id: str) -> Portfolio:
    portfolio = db.scalar(select(Portfolio).where(Portfolio.id == portfolio_id).with_for_update())
    if not portfolio:
        raise AppError(404, "NOT_FOUND", "Carteira não encontrada.")
    return portfolio


def append_event(
    db: Session,
    payload: TransactionCreate,
    actor: User,
    portfolio: Portfolio,
    state: LedgerState,
) -> Transaction:
    """Caller holds portfolio lock and validates chronological append and capacity."""
    if payload.instrument_id and not db.get(Instrument, str(payload.instrument_id)):
        raise AppError(404, "NOT_FOUND", "Ativo não encontrado.")
    event = as_event(payload)
    postings = apply_event(state, event)
    row = Transaction(
        portfolio_id=portfolio.id,
        owner_id=portfolio.owner_id,
        broker_account_id=portfolio.account_id,
        instrument_id=event.instrument_id,
        event_type=payload.event_type,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        gross_amount=event_gross(event),
        fees=payload.fees,
        taxes=payload.taxes,
        trade_date=payload.trade_date,
        settlement_date=payload.settlement_date,
        source=payload.source,
        external_id=payload.external_id,
        idempotency_key=payload.idempotency_key,
        payload_hash=canonical_hash(payload),
        notes=payload.notes,
        created_by=actor.id,
    )
    db.add(row)
    db.flush()
    db.add_all(
        [
            JournalEntry(
                transaction_id=row.id,
                account=p.account,
                amount=p.amount,
                instrument_id=p.instrument_id,
                quantity=p.quantity,
            )
            for p in postings
        ]
    )
    db.add(
        AuditEvent(actor_id=actor.id, action="record", entity_type="transaction", entity_id=row.id)
    )
    return row


def record_transaction(
    db: Session, payload: TransactionCreate, actor: User
) -> tuple[Transaction, bool]:
    portfolio = lock_portfolio(db, str(payload.portfolio_id))
    duplicate = db.scalar(
        select(Transaction).where(
            Transaction.portfolio_id == portfolio.id,
            Transaction.idempotency_key == payload.idempotency_key,
        )
    )
    if not duplicate and payload.external_id:
        duplicate = db.scalar(
            select(Transaction).where(
                Transaction.portfolio_id == portfolio.id,
                Transaction.source == payload.source,
                Transaction.external_id == payload.external_id,
            )
        )
    if duplicate:
        if duplicate.payload_hash != canonical_hash(payload):
            raise AppError(409, "CONFLICT", "A mesma identificação já foi usada com outros dados.")
        return duplicate, False
    rows = event_rows(db, [portfolio.id], today(), for_append=True)
    if rows and payload.trade_date < rows[-1].trade_date:
        raise AppError(
            409,
            "CHRONOLOGY_CONFLICT",
            "Registre os eventos em ordem cronológica. Retificação histórica ainda pendente.",
        )
    return append_event(db, payload, actor, portfolio, replay(rows)), True
