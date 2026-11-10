"""Handmade XLSX through HTTP, immutable previews and the real PostgreSQL ledger."""

import builtins
import zipfile
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from io import BytesIO
from xml.sax.saxutils import escape

from test_imports import confirm, preview, source, upload

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
DAY = "2026-01-05"
EXCEL_DAY = str((date(2026, 1, 5) - date(1899, 12, 30)).days)
HEADERS = ["tipo", "data", "valor", "quantidade", "preco", "ticker", "referencia"]
CONFIG = {
    "mapping": dict(
        zip(
            [
                "event_type",
                "trade_date",
                "gross_amount",
                "quantity",
                "unit_price",
                "ticker",
                "external_id",
            ],
            HEADERS,
            strict=True,
        )
    ),
    "decimal_separator": ",",
    "date_format": "YYYY-MM-DD",
    "exchange": "TEST",
}


@dataclass(frozen=True)
class Number:
    raw: str
    date_style: bool = False


@dataclass(frozen=True)
class Formula:
    expression: str
    cache: str


def workbook(rows):
    """Keep test numbers as raw XML strings: a spreadsheet writer may round them."""
    xml_rows = []
    for number, values in enumerate([HEADERS, *rows], 1):
        cells = []
        for column, value in enumerate(values):
            reference = f"{chr(ord('A') + column)}{number}"
            if isinstance(value, Number):
                cells.append(
                    f'<c r="{reference}" s="{int(value.date_style)}"><v>{escape(value.raw)}</v></c>'
                )
            elif isinstance(value, Formula):
                cells.append(
                    f'<c r="{reference}"><f>{escape(value.expression)}</f>'
                    f"<v>{escape(value.cache)}</v></c>"
                )
            elif value is not None:
                cells.append(
                    f'<c r="{reference}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
                )
        xml_rows.append(f'<row r="{number}">' + "".join(cells) + "</row>")
    parts = {
        "[Content_Types].xml": f'<Types xmlns="{CT}"><Override PartName="/xl/workbook.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        f'<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-'
        'officedocument.spreadsheetml.worksheet+xml"/>'
        f'<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/></Types>',
        "_rels/.rels": f'<Relationships xmlns="{PKG}"><Relationship Id="root" '
        f'Type="{REL}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{NS}" xmlns:r="{REL}">'
        '<workbookPr date1904="0"/><sheets><sheet name="Operações" sheetId="1" r:id="sheet"/>'
        "</sheets></workbook>",
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{PKG}">'
        f'<Relationship Id="sheet" Type="{REL}/worksheet" Target="worksheets/sheet1.xml"/>'
        f'<Relationship Id="styles" Type="{REL}/styles" Target="styles.xml"/></Relationships>',
        "xl/styles.xml": f'<styleSheet xmlns="{NS}"><cellXfs count="2">'
        '<xf numFmtId="0"/><xf numFmtId="14"/></cellXfs></styleSheet>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{NS}"><sheetData>'
        + "".join(xml_rows)
        + "</sheetData></worksheet>",
    }
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    return output.getvalue()


def deposit(amount, external_id):
    return [
        "deposit",
        Number(EXCEL_DAY, date_style=True),
        amount,
        Number("0"),
        Number("0"),
        None,
        external_id,
    ]


def upload_workbook(client, portfolio, rows):
    content = workbook(rows)
    batch = upload(client, portfolio, source(client), content, filename="operacoes.xlsx")
    assert client.get(batch["original_url"]).content == content
    # A second HTTP read exercises the stored dataclass/asdict JSON contract.
    stored = client.get(f"/api/v1/imports/{batch['id']}")
    assert stored.status_code == 200, stored.text
    assert stored.json()["sample"] == batch["sample"]
    return batch


def exclude(row_number, reason):
    return {**CONFIG, "decisions": [{"row_number": row_number, "action": "skip", "reason": reason}]}


def test_xlsx_numeric_text_locale_dates_and_eight_decimals_reach_the_ledger(
    client, portfolio, instrument
):
    batch = upload_workbook(
        client,
        portfolio,
        [
            deposit(Number("1.000"), "N1"),
            deposit("10,25", "T1"),
            [
                "buy",
                DAY,
                Number("2.00"),
                Number("1.00000001"),
                Number("2.00000001"),
                instrument["ticker"],
                "B1",
            ],
        ],
    )
    samples = batch["sample"]
    assert samples[0]["values"]["valor"] == "1.000"
    assert "valor" in samples[0]["numeric_columns"]
    assert samples[0]["values"]["data"] == DAY
    assert "data" not in samples[0]["numeric_columns"]
    assert samples[1]["values"]["valor"] == "10,25"
    assert "valor" not in samples[1]["numeric_columns"]
    snapshot = preview(client, batch, CONFIG)
    assert snapshot["summary"]["ready"] == 3, snapshot
    assert Decimal(snapshot["summary"]["cash_after"]) == Decimal("9.25")
    assert snapshot["summary"]["period_start"] == DAY
    assert snapshot["rows"][2]["normalized"]["quantity"] == "1.00000001"
    assert snapshot["rows"][2]["normalized"]["unit_price"] == "2.00000001"
    assert client.get("/api/v1/transactions").json()["total"] == 0
    receipt = confirm(client, batch, snapshot)
    assert receipt.status_code == 201, receipt.text
    transactions = client.get("/api/v1/transactions").json()
    assert transactions["total"] == 3
    buy = next(item for item in transactions["items"] if item["event_type"] == "buy")
    assert isinstance(buy["quantity"], str)
    assert Decimal(buy["quantity"]) == Decimal("1.00000001")
    assert Decimal(buy["unit_price"]) == Decimal("2.00000001")
    assert buy["trade_date"] == DAY
    dashboard = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).json()
    assert Decimal(dashboard["summary"]["cash"]) == Decimal("9.25")
    assert Decimal(dashboard["positions"][0]["quantity"]) == Decimal("1.00000001")


def test_xlsx_text_dot_decimal_is_quarantined_under_comma_locale(client, portfolio):
    batch = upload_workbook(
        client, portfolio, [deposit(Number("1.000"), "N1"), deposit("1.000", "T1")]
    )
    first = preview(client, batch, CONFIG)
    assert first["rows"][0]["status"] == "ready"
    assert first["rows"][1]["status"] == "quarantined"
    assert first["rows"][1]["raw"]["valor"] == "1.000"
    assert Decimal(first["summary"]["cash_after"]) == Decimal("1")
    assert confirm(client, batch, first).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 0
    resolved = preview(
        client, batch, exclude(3, "Separador ambíguo; excluído para revisão do extrato")
    )
    receipt = confirm(client, batch, resolved)
    assert receipt.status_code == 201, receipt.text
    assert [item["status"] for item in receipt.json()["results"]] == ["ready", "excluded"]
    items = client.get("/api/v1/transactions").json()["items"]
    assert len(items) == 1
    assert Decimal(items[0]["gross_amount"]) == Decimal("1")


def test_xlsx_formula_requires_explicit_exclusion_and_never_uses_its_cache(client, portfolio):
    batch = upload_workbook(
        client,
        portfolio,
        [deposit(Number("100.10"), "D1"), deposit(Formula("1+1", "9999999.99"), "F1")],
    )
    first = preview(client, batch, CONFIG)
    assert first["summary"]["ready"] == first["summary"]["quarantined"] == 1
    formula = first["rows"][1]
    assert formula["raw"]["valor"] is None
    assert any("Fórmula" in error for error in formula["errors"])
    assert Decimal(first["summary"]["cash_after"]) == Decimal("100.10")
    assert confirm(client, batch, first).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 0
    reason = "Fórmula excluída; considerar somente a operação documentada"
    resolved = preview(client, batch, exclude(3, reason))
    assert resolved["rows"][1]["decision"]["reason"] == reason
    assert resolved["summary"]["can_commit"]
    receipt = confirm(client, batch, resolved)
    assert receipt.status_code == 201, receipt.text
    assert receipt.json()["results"][1] == {
        "row_number": 3,
        "status": "excluded",
        "transaction_id": None,
    }
    assert client.get(f"/api/v1/snapshots/{first['id']}").json() == first
    transactions = client.get("/api/v1/transactions").json()
    assert transactions["total"] == 1
    assert Decimal(transactions["items"][0]["gross_amount"]) == Decimal("100.10")


def test_xlsx_eighteen_digit_quantity_survives_preview_confirmation_and_postgresql(
    client, portfolio, instrument
):
    exact_quantity = "1234567890.12345678"
    batch = upload_workbook(
        client,
        portfolio,
        [
            deposit(Number("100.00"), "D1"),
            [
                "buy",
                Number(EXCEL_DAY, date_style=True),
                Number("12.35"),
                Number(exact_quantity),
                Number("0.00000001"),
                instrument["ticker"],
                "B1",
            ],
        ],
    )
    assert batch["sample"][1]["values"]["quantidade"] == exact_quantity
    snapshot = preview(client, batch, CONFIG)
    assert snapshot["summary"]["can_commit"], snapshot
    assert snapshot["rows"][1]["normalized"]["quantity"] == exact_quantity
    assert isinstance(snapshot["rows"][1]["normalized"]["unit_price"], str)
    assert Decimal(snapshot["rows"][1]["normalized"]["unit_price"]) == Decimal("0.00000001")
    receipt = confirm(client, batch, snapshot)
    assert receipt.status_code == 201, receipt.text
    transactions = client.get("/api/v1/transactions").json()["items"]
    buy = next(item for item in transactions if item["event_type"] == "buy")
    assert isinstance(buy["quantity"], str)
    assert Decimal(buy["quantity"]) == Decimal(exact_quantity)
    assert Decimal(buy["unit_price"]) == Decimal("0.00000001")
    dashboard = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).json()
    assert Decimal(dashboard["positions"][0]["quantity"]) == Decimal(exact_quantity)
    assert Decimal(dashboard["positions"][0]["cost_basis"]) == Decimal("12.35")
    assert Decimal(dashboard["summary"]["cash"]) == Decimal("87.65")


def test_xlsx_extreme_exponents_are_quarantined_before_decimal_expansion(
    client, portfolio, monkeypatch
):
    from hub_api import import_service

    def bounded_format(value, spec=""):
        # Fail safely on a regression instead of allocating enormous decimal text.
        if isinstance(value, Decimal):
            assert abs(value.as_tuple().exponent) <= 50, "Exponent expanded before validation"
        return builtins.format(value, spec)

    monkeypatch.setattr(import_service, "format", bounded_format, raising=False)
    exponents = ["1E+999999999999999", "1E-999999999999999"]
    batch = upload_workbook(
        client, portfolio, [deposit(Number(value), f"X{i}") for i, value in enumerate(exponents)]
    )
    assert [r["values"]["valor"] for r in batch["sample"]] == exponents
    assert all("valor" in r["numeric_columns"] for r in batch["sample"])
    snapshot = preview(client, batch, CONFIG)
    assert snapshot["summary"]["quarantined"] == 2
    assert snapshot["summary"]["ready"] == 0
    assert all(any("limites" in error for error in r["errors"]) for r in snapshot["rows"])
    response = confirm(client, batch, snapshot)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNRESOLVED_ROWS"
    assert client.get("/api/v1/transactions").json()["total"] == 0
