"""Regressions for importer reconciliation, bounded previews and receipt consistency."""

import csv
import json
import uuid
import zipfile
from decimal import Decimal
from io import BytesIO, StringIO
from xml.sax.saxutils import escape

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from test_imports import CONFIG, DAY, HEADER, confirm, preview, source, upload


def upload_rows(client, portfolio, source_id, rows):
    stream = StringIO(newline="")
    columns = list(rows[0])
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter=";", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    batch = upload(client, portfolio, source_id, stream.getvalue().encode())
    return batch, {"mapping": {column: column for column in columns}}


def deposit_row(external_id, amount="100"):
    return {
        "event_type": "deposit",
        "trade_date": DAY,
        "gross_amount": amount,
        "external_id": external_id,
    }


def cash(client, portfolio):
    response = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]})
    assert response.status_code == 200, response.text
    return Decimal(response.json()["summary"]["cash"])


def manual_deposit(client, portfolio):
    response = client.post(
        "/api/v1/transactions",
        json={
            "portfolio_id": portfolio["id"],
            "event_type": "deposit",
            "trade_date": DAY,
            "gross_amount": "100",
            "idempotency_key": str(uuid.uuid4()),
        },
    )
    assert response.status_code == 201, response.text


def external_id_workbook(raw_id, *, numeric=True):
    """Build raw OOXML in memory so no writer rounds or reformats the identifier."""
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    pkg = "http://schemas.openxmlformats.org/package/2006/relationships"
    ct = "http://schemas.openxmlformats.org/package/2006/content-types"

    def cell(reference, value, is_number=False):
        if is_number:
            return f'<c r="{reference}" t="n"><v>{escape(value)}</v></c>'
        return f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'

    headers = HEADER.strip().split(";")
    heading = "".join(cell(f"{chr(65 + i)}1", name) for i, name in enumerate(headers))
    values = ["deposit", DAY, "100", raw_id]
    body = "".join(
        cell(f"{chr(65 + i)}2", value, i == 2 or (i == 3 and numeric))
        for i, value in enumerate(values)
    )
    parts = {
        "[Content_Types].xml": f'<Types xmlns="{ct}">'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/></Types>',
        "_rels/.rels": f'<Relationships xmlns="{pkg}"><Relationship Id="root" '
        f'Type="{rel}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{ns}" xmlns:r="{rel}"><sheets>'
        '<sheet name="Dados" sheetId="1" r:id="sheet"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{pkg}"><Relationship Id="sheet" '
        f'Type="{rel}/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{ns}"><sheetData>'
        f'<row r="1">{heading}</row><row r="2">{body}</row></sheetData></worksheet>',
    }
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    return output.getvalue()


@pytest.mark.parametrize(
    ("raw_id", "canonical_id"),
    [
        ("1E+2", "100"),
        ("100.000", "100"),
        ("1.2345678901234567890123456789E+29", "123456789012345678901234567890"),
    ],
)
def test_numeric_xlsx_id_reuses_csv_transaction_exactly(client, portfolio, raw_id, canonical_id):
    origin = source(client)
    first, config = upload_rows(client, portfolio, origin, [deposit_row(canonical_id)])
    original_receipt = confirm(client, first, preview(client, first, config))
    assert original_receipt.status_code == 201, original_receipt.text
    transaction_id = original_receipt.json()["results"][0]["transaction_id"]

    content = external_id_workbook(raw_id)
    second = upload(client, portfolio, origin, content, filename="numeric-id.xlsx")
    assert "external_id" in second["sample"][0]["numeric_columns"]
    snapshot = preview(client, second)
    row = snapshot["rows"][0]
    assert row["raw"]["external_id"] == raw_id
    assert row["normalized"]["external_id"] == canonical_id
    assert row["status"] == "duplicate"
    assert row["transaction_id"] == transaction_id
    receipt = confirm(client, second, snapshot)
    assert receipt.status_code == 201, receipt.text
    assert receipt.json()["results"][0]["transaction_id"] == transaction_id
    assert client.get("/api/v1/transactions").json()["total"] == 1
    assert cash(client, portfolio) == Decimal("100")
    assert client.get(second["original_url"]).content == content


@pytest.mark.parametrize("mode", ["text", "edit"])
@pytest.mark.parametrize("opaque_id", ["00100", "1E+2"])
def test_text_and_edited_ids_are_not_numeric_aliases(client, portfolio, mode, opaque_id):
    origin = source(client)
    first, config = upload_rows(client, portfolio, origin, [deposit_row("100")])
    assert confirm(client, first, preview(client, first, config)).status_code == 201
    content = external_id_workbook(opaque_id if mode == "text" else "1E+2", numeric=mode == "edit")
    batch = upload(client, portfolio, origin, content, filename=f"{mode}-id.xlsx")
    config = {"mapping": dict(CONFIG["mapping"])}
    if mode == "edit":
        config["edits"] = [
            {"row_number": 2, "values": {"external_id": opaque_id}, "reason": "ID textual conferido"}
        ]
    snapshot = preview(client, batch, config)
    assert snapshot["rows"][0]["normalized"]["external_id"] == opaque_id
    assert snapshot["rows"][0]["status"] == "ready"
    assert confirm(client, batch, snapshot).status_code == 201
    transactions = client.get("/api/v1/transactions").json()
    assert transactions["total"] == 2
    assert {item["external_id"] for item in transactions["items"]} == {"100", opaque_id}
    assert cash(client, portfolio) == Decimal("200")


def test_fractional_numeric_external_id_is_not_rounded_into_an_identity(client, portfolio):
    batch = upload(
        client, portfolio, source(client), external_id_workbook("1.5"), filename="fraction-id.xlsx"
    )
    snapshot = preview(client, batch)
    assert snapshot["rows"][0]["status"] == "quarantined"
    assert not snapshot["summary"]["can_commit"]
    assert confirm(client, batch, snapshot).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 0


@pytest.mark.parametrize("omitted", ["settlement_date", "fees", "taxes"])
def test_unmapped_optional_fields_cannot_hide_duplicates_or_weaken_id_conflicts(
    client, portfolio, instrument, omitted
):
    manual_deposit(client, portfolio)
    origin = source(client)
    execution = {
        "event_type": "buy",
        "trade_date": DAY,
        "settlement_date": "2026-01-07",
        "instrument_id": instrument["id"],
        "quantity": "1",
        "unit_price": "10",
        "gross_amount": "10",
        "fees": "1",
        "taxes": "0.25",
        "external_id": "B1",
    }
    first, config = upload_rows(client, portfolio, origin, [execution])
    receipt = confirm(client, first, preview(client, first, config))
    assert receipt.status_code == 201, receipt.text
    transaction_id = receipt.json()["results"][0]["transaction_id"]

    # The optional value remains in the original file but is deliberately not mapped.
    overlap, config = upload_rows(client, portfolio, origin, [{**execution, "external_id": ""}])
    config["mapping"].pop(omitted)
    snapshot = preview(client, overlap, config)
    row = snapshot["rows"][0]
    assert row["raw"][omitted] == execution[omitted]
    assert row["status"] == "needs_review"
    assert row["candidate_count"] == 1
    assert row["candidates"] == [{"transaction_id": transaction_id, "row_number": None}]
    assert not snapshot["summary"]["can_commit"]
    assert confirm(client, overlap, snapshot).status_code == 422

    # Same provider ID must still reject changed settlement/charges, not auto-deduplicate.
    conflict, config = upload_rows(
        client, portfolio, origin, [{**execution, "gross_amount": "10.00"}]
    )
    config["mapping"].pop(omitted)
    snapshot = preview(client, conflict, config)
    assert snapshot["rows"][0]["status"] == "quarantined"
    assert snapshot["rows"][0]["errors"]
    assert confirm(client, conflict, snapshot).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 2
    assert cash(client, portfolio) == Decimal("88.75")
    positions = client.get("/api/v1/dashboard").json()["positions"]
    assert Decimal(positions[0]["quantity"]) == Decimal("1")


def test_mapped_zero_gross_is_quarantined_before_posting_or_duplicate_detection(
    client, portfolio, instrument
):
    manual_deposit(client, portfolio)
    origin = source(client)
    execution = {
        "event_type": "buy",
        "trade_date": DAY,
        "instrument_id": instrument["id"],
        "quantity": "1",
        "unit_price": "10",
        "gross_amount": "0",
        "external_id": "B1",
    }
    batch, config = upload_rows(client, portfolio, origin, [execution])
    rejected = preview(client, batch, config)
    assert rejected["rows"][0]["status"] == "quarantined"
    assert confirm(client, batch, rejected).status_code == 422
    assert cash(client, portfolio) == Decimal("100")
    assert client.get("/api/v1/transactions").json()["total"] == 1

    config["mapping"].pop("gross_amount")
    calculated = preview(client, batch, config)
    assert calculated["rows"][0]["status"] == "ready"
    assert Decimal(calculated["rows"][0]["calculated_gross_amount"]) == Decimal("10")
    assert Decimal(calculated["summary"]["cash_after"]) == Decimal("90")
    assert confirm(client, batch, calculated).status_code == 201
    assert client.get(f"/api/v1/snapshots/{rejected['id']}").json() == rejected

    other, config = upload_rows(client, portfolio, origin, [{**execution, "gross_amount": "0.00"}])
    repeated = preview(client, other, config)
    assert repeated["rows"][0]["status"] == "quarantined"
    assert confirm(client, other, repeated).status_code == 422
    transactions = client.get("/api/v1/transactions").json()
    assert transactions["total"] == 2
    buy = next(item for item in transactions["items"] if item["event_type"] == "buy")
    assert Decimal(buy["gross_amount"]) == Decimal("10")
    assert cash(client, portfolio) == Decimal("90")


@pytest.mark.parametrize("endpoint", ["detail", "lineage"])
def test_concurrent_confirmation_never_pairs_receipt_with_another_preview(
    client, app, portfolio, endpoint
):
    batch, config = upload_rows(client, portfolio, source(client), [deposit_row("D1")])
    original = preview(client, batch, config)
    changed = {
        **config,
        "edits": [
            {"row_number": 2, "values": {"gross_amount": "200"}, "reason": "Valor conferido"}
        ],
    }
    injected = False
    committed = {}
    path = f"/api/v1/imports/{batch['id']}" if endpoint == "detail" else "/api/v1/lineage"
    params = {} if endpoint == "detail" else {"import_id": batch["id"]}

    with TestClient(app, cookies=dict(client.cookies), headers={"X-Hub-Request": "1"}) as writer:

        def after_read(conn, cursor, statement, parameters, context, executemany):
            nonlocal injected
            sql = statement.lower()
            if injected or not sql.lstrip().startswith("select"):
                return
            if "from import_previews" not in sql and "from import_receipts" not in sql:
                return
            # The first result has been selected. Do not assume which table is read first.
            injected = True
            revised = preview(writer, batch, changed)
            receipt = confirm(writer, batch, revised)
            assert receipt.status_code == 201, receipt.text
            committed.update(preview=revised, receipt=receipt.json())

        event.listen(app.state.engine, "after_cursor_execute", after_read)
        try:
            response = client.get(path, params=params)
        finally:
            event.remove(app.state.engine, "after_cursor_execute", after_read)
        assert response.status_code == 200, response.text
        assert injected, "The competing confirmation must occur during the read."
        result = response.json()
        metadata = result if endpoint == "detail" else result["import"]
        receipt = result["receipt"]
        if receipt is not None:
            assert metadata["status"] == "committed"
            assert metadata["latest_preview_id"] == receipt["preview_id"]
            assert metadata["summary"] == committed["preview"]["summary"]
            if endpoint == "detail":
                assert result["preview"]["id"] == receipt["preview_id"]
        else:
            # A draft observed before confirmation is valid; mixed confirmed metadata is not.
            assert metadata["status"] == "previewed"
            snapshots = {item["id"]: item for item in (original, committed["preview"])}
            assert metadata["summary"] == snapshots[metadata["latest_preview_id"]]["summary"]

        stable = client.get(path, params=params)
        assert stable.status_code == 200, stable.text
        result = stable.json()
        metadata = result if endpoint == "detail" else result["import"]
        assert metadata["status"] == "committed"
        assert result["receipt"] == committed["receipt"]
        assert metadata["latest_preview_id"] == committed["preview"]["id"]
        assert metadata["summary"] == committed["preview"]["summary"]
        if endpoint == "detail":
            assert result["preview"] == committed["preview"]
        assert confirm(client, batch, committed["preview"]).json() == committed["receipt"]
        assert client.get(f"/api/v1/snapshots/{original['id']}").json() == original
        assert cash(client, portfolio) == Decimal("200")


def test_candidates_are_bounded_without_truncating_ambiguity_checks(client, portfolio):
    origin = source(client)
    initial, config = upload_rows(
        client, portfolio, origin, [deposit_row(f"execution-{i}") for i in range(201)]
    )
    first = preview(client, initial, config)
    assert first["summary"]["ready"] == 201
    receipt = confirm(client, initial, first)
    assert receipt.status_code == 201, receipt.text
    existing_ids = {item["transaction_id"] for item in receipt.json()["results"]}

    batch, config = upload_rows(client, portfolio, origin, [deposit_row("") for _ in range(500)])
    snapshot = preview(client, batch, config)
    assert snapshot["summary"]["needs_review"] == 500
    assert not snapshot["summary"]["can_commit"]
    for row in snapshot["rows"]:
        assert row["candidate_count"] == 201
        assert len(row["candidates"]) == 20
        candidates = {item["transaction_id"] for item in row["candidates"]}
        assert len(candidates) == 20
        assert candidates <= existing_ids
    assert client.get(f"/api/v1/snapshots/{snapshot['id']}").json() == snapshot
    assert confirm(client, batch, snapshot).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 201
    assert cash(client, portfolio) == Decimal("20100")

    # The ambiguous manual event comes after all 201 numbered provider executions.
    manual_deposit(client, portfolio)
    other, config = upload_rows(client, portfolio, origin, [deposit_row("new-execution")])
    last = preview(client, other, config)
    row = last["rows"][0]
    assert row["candidate_count"] == 202
    assert len(row["candidates"]) == 20
    assert {item["transaction_id"] for item in row["candidates"]} <= existing_ids
    assert row["status"] == "needs_review"
    assert confirm(client, other, last).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 202


@pytest.mark.parametrize("invalid", ["\x00", "\ud800", "\udfff"], ids=["nul", "high", "low"])
@pytest.mark.parametrize("field", ["external_id", "notes", "reason", "event_values"])
def test_invalid_import_text_is_rejected_before_a_preview_is_persisted(
    client, portfolio, invalid, field
):
    batch, config = upload_rows(client, portfolio, source(client), [deposit_row("D1")])
    bad_text = "antes" + invalid + "depois"
    if field == "event_values":
        config["event_values"] = {bad_text: "deposit"}
    else:
        edit = {"row_number": 2, "values": {"notes": "Conferido"}, "reason": "Valor conferido"}
        if field == "reason":
            edit["reason"] = bad_text
        else:
            edit["values"] = {field: bad_text}
        config["edits"] = [edit]
    # Escapes must reach the server: httpx's ordinary JSON encoding rejects lone surrogates.
    response = client.post(
        f"/api/v1/imports/{batch['id']}/preview",
        content=json.dumps(config, ensure_ascii=True).encode("ascii"),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422, response.text
    assert client.get("/api/v1/snapshots", params={"import_id": batch["id"]}).json()["total"] == 0
    detail = client.get(f"/api/v1/imports/{batch['id']}").json()
    assert detail["status"] == "uploaded"
    assert detail["preview"] is None and detail["receipt"] is None
    assert client.get("/api/v1/transactions").json()["total"] == 0


def test_valid_unicode_edits_survive_confirmation(client, portfolio):
    batch, config = upload_rows(client, portfolio, source(client), [deposit_row("D1")])
    note = "Conferido: café 🔎"
    config["edits"] = [{"row_number": 2, "values": {"notes": note}, "reason": "Revisão válida"}]
    response = client.post(
        f"/api/v1/imports/{batch['id']}/preview",
        content=json.dumps(config, ensure_ascii=True).encode("ascii"),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 201, response.text
    snapshot = response.json()
    assert snapshot["rows"][0]["status"] == "ready"
    assert snapshot["rows"][0]["normalized"]["notes"] == note
    assert confirm(client, batch, snapshot).status_code == 201
    assert client.get("/api/v1/transactions").json()["items"][0]["notes"] == note
