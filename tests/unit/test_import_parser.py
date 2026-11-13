"""Synthetic CSV and handmade OOXML: exactness, quarantine and resource limits."""

import csv
import json
import struct
import zipfile
import zlib
from dataclasses import asdict
from io import BytesIO, StringIO
from xml.sax.saxutils import escape, quoteattr

import pytest
from hub_api.import_parser import ParsedRow, ParsedTable, ParseError, parse_table

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
MAIN_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"


def text_cell(ref, text, style=None):
    attributes = f' s="{style}"' if style is not None else ""
    return (
        f'<c r="{ref}" t="inlineStr"{attributes}>'
        f'<is><t xml:space="preserve">{escape(text)}</t></is></c>'
    )


def number_cell(ref, value, style=None):
    attributes = f' s="{style}"' if style is not None else ""
    return f'<c r="{ref}"{attributes}><v>{escape(value)}</v></c>'


def row(number, *cells, attributes=""):
    return f'<row r="{number}" {attributes}>' + "".join(cells) + "</row>"


def worksheet(rows, extra=""):
    return f'<worksheet xmlns="{NS}"><sheetData>{rows}</sheetData>{extra}</worksheet>'


def styles(*formats, custom="", bases=""):
    return (
        f'<styleSheet xmlns="{NS}">{custom}{bases}<cellXfs>'
        + "".join(f'<xf numFmtId="{fmt}"/>' for fmt in formats)
        + "</cellXfs></styleSheet>"
    )


def package(sheets=None, *, style_xml=None, shared=None, epoch="0"):
    if sheets is None:
        sheets = {
            "Dados": worksheet(
                row(1, text_cell("A1", "valor")) + row(2, number_cell("A2", "123.45"))
            )
        }
    parts = {
        "[Content_Types].xml": f'<Types xmlns="{CT}">'
        f'<Override PartName="/xl/workbook.xml" ContentType="{MAIN_TYPE}"/></Types>',
        "_rels/.rels": f'<Relationships xmlns="{PKG}">'
        f'<Relationship Id="root" Type="{REL}/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>",
    }
    sheet_tags, relationships = [], []
    for index, (name, xml) in enumerate(sheets.items(), 1):
        sheet_tags.append(f'<sheet name={quoteattr(name)} sheetId="{index}" r:id="s{index}"/>')
        relationships.append(
            f'<Relationship Id="s{index}" Type="{REL}/worksheet" '
            f'Target="worksheets/sheet{index}.xml"/>'
        )
        parts[f"xl/worksheets/sheet{index}.xml"] = xml
    for name, xml, kind in [
        ("styles.xml", style_xml, "styles"),
        ("sharedStrings.xml", shared, "sharedStrings"),
    ]:
        if xml is not None:
            parts[f"xl/{name}"] = xml
            relationships.append(f'<Relationship Id="{kind}" Type="{REL}/{kind}" Target="{name}"/>')
    parts["xl/workbook.xml"] = (
        f'<workbook xmlns="{NS}" xmlns:r="{REL}">'
        f'<workbookPr date1904="{epoch}"/><sheets>' + "".join(sheet_tags) + "</sheets></workbook>"
    )
    parts["xl/_rels/workbook.xml.rels"] = (
        f'<Relationships xmlns="{PKG}">' + "".join(relationships) + "</Relationships>"
    )
    return parts


def zipped(parts, compression=zipfile.ZIP_DEFLATED):
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=compression) as archive:
        for name, content in parts.items():
            # Keep deliberately malformed names in the actual ZIP bytes even on
            # Windows, where ZipInfo's constructor normalizes path separators.
            info = zipfile.ZipInfo(name)
            info.filename = name
            archive.writestr(info, content, compress_type=compression)
    return output.getvalue()


def xlsx(rows, *, extra="", **kwargs):
    return zipped(package({"Dados": worksheet(rows, extra)}, **kwargs))


def test_dataclass_contract_is_json_serializable_and_defaults_are_independent():
    first, second = ParsedRow(2, {"a": None}, []), ParsedRow(3, {"a": "0"}, [])
    first.numeric_columns.append("a")
    assert second.numeric_columns == []
    result = ParsedTable(["a"], [first, second], None)
    assert json.loads(json.dumps(asdict(result))) == {
        "headers": ["a"],
        "sheet": None,
        "rows": [
            {"number": 2, "values": {"a": None}, "errors": [], "numeric_columns": ["a"]},
            {"number": 3, "values": {"a": "0"}, "errors": [], "numeric_columns": []},
        ],
    }
    assert issubclass(ParseError, ValueError)


def test_csv_bom_quoting_locale_nulls_and_physical_line_numbers():
    content = (
        "\ufeff data ;valor;nota\r\n"
        '2026-11-10;"1.234,567890123456789";"a;b ""sim""\r\nsegunda"\r\n'
        "2026-11-11;0;\r\n"
        ";;\r\n"
        '2026-11-12;  ;" texto "\r\n'
    ).encode()
    result = parse_table(content, "extrato.CSV")
    assert result.headers == ["data", "valor", "nota"]
    assert result.sheet is None
    assert [r.number for r in result.rows] == [2, 4, 6]
    assert result.rows[0].values == {
        "data": "2026-11-10",
        "valor": "1.234,567890123456789",
        "nota": 'a;b "sim"\r\nsegunda',
    }
    assert result.rows[1].values["valor"] == "0"
    assert result.rows[1].values["nota"] is None
    assert result.rows[2].values == {"data": "2026-11-12", "valor": None, "nota": " texto "}
    assert all(not r.errors and not r.numeric_columns for r in result.rows)


@pytest.mark.parametrize("delimiter", [";", ",", "\t"])
def test_csv_round_trips_csv_writer_special_characters(delimiter):
    values = ["1.000", "+.5", "-1e-10", 'a"b', "a;b,c\td", "a\rb\nc\r\nd", " ", ""]
    stream = StringIO(newline="")
    writer = csv.writer(stream, delimiter=delimiter)
    writer.writerow([f"col{i}" for i in range(len(values))])
    writer.writerow(values)
    parsed = parse_table(stream.getvalue().encode(), "a.csv", delimiter=delimiter)
    assert list(parsed.rows[0].values.values()) == values[:-2] + [None, None]
    assert parsed.rows[0].numeric_columns == []


@pytest.mark.parametrize("encoding", ["cp1252", "windows-1252"])
def test_csv_cp1252_must_be_selected_explicitly(encoding):
    content = "ação;preço\nPETR4;1.000,20".encode("cp1252")
    with pytest.raises(ParseError, match="Codificação"):
        parse_table(content, "a.csv")
    result = parse_table(content, "a.csv", encoding=encoding)
    assert result.rows[0].values == {"ação": "PETR4", "preço": "1.000,20"}


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "UTF_8"])
def test_csv_utf8_bom_is_removed_with_utf8_aliases(encoding):
    assert parse_table(b"\xef\xbb\xbfa\n1", "a.csv", encoding=encoding).headers == ["a"]


@pytest.mark.parametrize("content", [b'a\n"unfinished', b'a\na"b', b'a\n"b"x', b'a\n"b" '])
def test_csv_rejects_ambiguous_quote_grammar(content):
    with pytest.raises(ParseError, match="CSV inv"):
        parse_table(content, "a.csv")


def test_csv_wrong_row_lengths_are_quarantined_and_missing_cells_are_null():
    result = parse_table(b"a;b\n1\n2;3;4\n5;6", "a.csv")
    assert result.rows[0].values == {"a": "1", "b": None}
    assert result.rows[1].values == {"a": "2", "b": "3"}
    assert "recebidas 1" in result.rows[0].errors[0]
    assert "recebidas 3" in result.rows[1].errors[0]
    assert not result.rows[2].errors


@pytest.mark.parametrize(
    "content, match",
    [
        (b"a;;c\n1;2;3", "Cabeçalho vazio"),
        (b"a;a\n1;2", "duplicados"),
        (b"a; A \n1;2", "duplicados"),
        (b"a;\n1;2", "Cabeçalho vazio"),
        (b"\n;;\n", "sem cabeçalho"),
        (b"", "vazio"),
    ],
)
def test_csv_rejects_invalid_headers(content, match):
    with pytest.raises(ParseError, match=match):
        parse_table(content, "a.csv")


@pytest.mark.parametrize(
    "options",
    [{"encoding": "latin-1"}, {"delimiter": "|"}, {"delimiter": ";;"}, {"sheet": "Dados"}],
)
def test_csv_rejects_unsupported_options(options):
    with pytest.raises(ParseError):
        parse_table(b"a\n1", "a.csv", **options)


def test_csv_row_limit_counts_only_nonempty_data_including_quarantine():
    content = b"a;b\n" + (b"\n;\n1;2\n" * 499) + b"last\n"
    result = parse_table(content, "a.csv")
    assert len(result.rows) == 500
    assert result.rows[-1].errors
    with pytest.raises(ParseError, match="500 linhas"):
        parse_table(content + b"1;2", "a.csv")


def test_csv_column_limit_and_empty_trailing_columns_are_bounded():
    header = ";".join(f"c{i}" for i in range(40))
    assert len(parse_table((header + "\n" + ";".join(["0"] * 40)).encode(), "a.csv").headers) == 40
    for content in [header + ";extra", "a\n" + ";" * 40]:
        with pytest.raises(ParseError, match="40 colunas"):
            parse_table(content.encode(), "a.csv")


def test_upload_limit_is_checked_before_decoding_or_decompression():
    for filename in ["a.csv", "a.xlsx"]:
        with pytest.raises(ParseError, match="2 MiB"):
            parse_table(b"x" * (2 * 1024 * 1024 + 1), filename)


@pytest.mark.parametrize("extension", ["xls", "xlsm", "zip", "txt", ""])
def test_unsupported_file_types_are_rejected(extension):
    with pytest.raises(ParseError, match="CSV ou XLSX"):
        parse_table(b"a\n1", "a." + extension)


def test_csv_headers_and_values_have_separate_length_bounds():
    assert parse_table(("h" * 200 + "\n" + "v" * 2000).encode(), "a.csv").rows
    for content, limit in [("h" * 201 + "\nx", 200), ("h\n" + "v" * 2001, 2000)]:
        with pytest.raises(ParseError, match=f"{limit} caracteres"):
            parse_table(content.encode(), "a.csv")


@pytest.mark.parametrize("content", [b"a\x00\n1", b'a\n"x\x00y"', b"a\n\x00"])
def test_csv_nul_is_rejected_even_inside_quoted_or_blank_cells(content):
    with pytest.raises(ParseError, match="NUL"):
        parse_table(content, "a.csv")


@pytest.mark.parametrize(
    "value",
    [
        "123456789012345678901234567890.12345678901234567890",
        "-1234567890.12345678901234567890",
        "+1.000",
        ".5",
        "-.5",
        "+.5",
        "0.000000000000000000000000000000000001",
        "-0.000",
        "1.2300E-20",
        "1E+999999",
    ],
)
def test_xlsx_raw_numeric_lexemes_are_exact_and_distinct_from_text(value):
    content = xlsx(
        row(1, text_cell("A1", "numero"), text_cell("B1", "texto"))
        + row(2, number_cell("A2", value), text_cell("B2", value))
    )
    result = parse_table(content, "precisao.xlsx")
    assert result.rows[0].values == {"numero": value, "texto": value}
    assert result.rows[0].numeric_columns == ["numero"]
    assert not result.rows[0].errors
    assert json.loads(json.dumps(asdict(result)))["rows"][0]["values"]["numero"] == value


def test_xlsx_shared_and_inline_rich_text_preserve_nulls_and_ignore_phonetics():
    shared = (
        f'<sst xmlns="{NS}"><si><t>ativo</t></si>'
        "<si><r><t>PET</t></r><r><t>R4</t></r><rPh><t>fonética</t></rPh></si>"
        "<si><t>  </t></si><si><t>_x005F_x0000_</t></si></sst>"
    )
    content = xlsx(
        row(1, '<c r="A1" t="s"><v>0</v></c>', text_cell("B1", "nota"))
        + row(2, '<c r="A2" t="s"><v>1</v></c>', text_cell("B2", " a & b "))
        + row(3, '<c r="A3" t="s"><v>2</v></c>', '<c r="B3" t="s"><v>3</v></c>'),
        shared=shared,
    )
    result = parse_table(content, "a.xlsx")
    assert result.rows[0].values == {"ativo": "PETR4", "nota": " a & b "}
    assert result.rows[1].values == {"ativo": None, "nota": "_x0000_"}
    assert not result.rows[0].numeric_columns


def test_xlsx_multiple_sheets_require_explicit_selection_with_available_names():
    parts = package(
        {
            "Compras": worksheet(row(1, text_cell("A1", "compra"))),
            "Vendas": worksheet(row(1, text_cell("A1", "venda"))),
        }
    )
    content = zipped(parts)
    for selected in [None, "ausente"]:
        with pytest.raises(ParseError, match="Compras, Vendas"):
            parse_table(content, "a.xlsx", sheet=selected)
    result = parse_table(content, "a.xlsx", sheet="Vendas")
    assert result == ParsedTable(["venda"], [], "Vendas")


def test_xlsx_formula_caches_and_excel_errors_are_quarantined():
    content = xlsx(
        row(1, text_cell("A1", "valor"), text_cell("B1", "id"))
        + row(2, '<c r="A2"><f>1+1</f><v>9999999.99</v></c>', number_cell("B2", "1"))
        + row(3, '<c r="A3"><f t="shared" si="0"/></c>')
        + row(4, '<c r="A4" t="e"><v>#DIV/0!</v></c>')
        + row(5, number_cell("A5", "2"))
    )
    result = parse_table(content, "a.xlsx")
    assert result.rows[0].values == {"valor": None, "id": "1"}
    assert result.rows[0].numeric_columns == ["id"]
    assert "Fórmula" in result.rows[0].errors[0]
    assert result.rows[1].errors
    assert "erro do Excel" in result.rows[2].errors[0]
    assert not result.rows[3].errors


def test_xlsx_array_formula_ranges_quarantine_cached_followers():
    content = xlsx(
        row(1, text_cell("A1", "valor"))
        + row(2, '<c r="A2"><f t="array" ref="A2:A3">1+1</f><v>2</v></c>')
        + row(3, number_cell("A3", "2"))
        + row(4, number_cell("A4", "3"))
    )
    rows = parse_table(content, "a.xlsx").rows
    assert all(any("intervalo de fórmula" in e for e in r.errors) for r in rows[:2])
    assert not rows[2].errors


def test_xlsx_merged_data_rows_are_quarantined_without_expanding_ranges():
    content = xlsx(
        row(1, text_cell("A1", "valor"), text_cell("B1", "nota"))
        + row(2, number_cell("A2", "1"))
        + row(3, text_cell("B3", "continua"))
        + row(4, number_cell("A4", "2")),
        extra='<mergeCells><mergeCell ref="A2:A3"/></mergeCells>',
    )
    rows = parse_table(content, "a.xlsx").rows
    assert all("Células mescladas na linha." in r.errors for r in rows[:2])
    assert not rows[2].errors
    # A range spanning the entire Excel grid must never allocate its cells.
    parts = package(
        {
            "Dados": worksheet(
                row(1, text_cell("A1", "v")) + row(2, number_cell("A2", "1")),
                '<mergeCells><mergeCell ref="A2:XFD1048576"/></mergeCells>',
            )
        }
    )
    huge = zipped(parts)
    assert parse_table(huge, "a.xlsx").rows[0].errors


@pytest.mark.parametrize(
    "header,extra",
    [
        (row(1, text_cell("A1", "v"), text_cell("C1", "c")), ""),
        (row(1, text_cell("A1", "v"), text_cell("B1", "V")), ""),
        (row(1, '<c r="A1"><f>1</f><v>1</v></c>'), ""),
        (row(1, text_cell("A1", "v")), '<mergeCells><mergeCell ref="A1:B1"/></mergeCells>'),
    ],
)
def test_xlsx_invalid_headers_reject_the_file(header, extra):
    with pytest.raises(ParseError, match="Cabeçalho"):
        parse_table(xlsx(header, extra=extra), "a.xlsx")


def test_xlsx_sparse_rows_nulls_and_styled_empty_rows_ignore_declared_dimensions():
    content = xlsx(
        row(1, text_cell("A1", "valor"), text_cell("B1", "nota"))
        + row(2, '<c r="A2" s="1"/>', '<c r="XFD2" s="1"/>')
        + row(3, text_cell("A3", "  "))
        + row(1_000_000, number_cell("A1000000", "0")),
        style_xml=styles(0, 14),
        extra='<dimension ref="A1:XFD1048576"/>',
    )
    rows = parse_table(content, "a.xlsx").rows
    assert [r.number for r in rows] == [1_000_000]
    assert rows[0].values == {"valor": "0", "nota": None}
    assert not rows[0].errors


def test_xlsx_extra_columns_are_quarantined_and_global_column_limit_is_enforced():
    header = row(1, text_cell("A1", "valor"))
    result = parse_table(xlsx(header + row(2, number_cell("B2", "1"))), "a.xlsx")
    assert result.rows[0].errors
    assert result.rows[0].values == {"valor": None}
    assert parse_table(xlsx(header + row(2, number_cell("AN2", "1"))), "a.xlsx").rows[0].errors
    with pytest.raises(ParseError, match="40 colunas"):
        parse_table(xlsx(header + row(2, number_cell("AO2", "1"))), "a.xlsx")


def test_xlsx_500_nonempty_rows_plus_styled_empty_rows_are_allowed():
    header = row(1, text_cell("A1", "valor"))
    data = "".join(row(n, number_cell(f"A{n}", "1")) for n in range(2, 502))
    empty = row(502, '<c r="A502" s="0"/>')
    assert len(parse_table(xlsx(header + data + empty), "a.xlsx").rows) == 500
    with pytest.raises(ParseError, match="500 linhas"):
        parse_table(xlsx(header + data + empty + row(503, number_cell("A503", "1"))), "a.xlsx")


@pytest.mark.parametrize(
    "epoch,serial,expected",
    [
        ("0", "1", "1900-01-01"),
        ("0", "59", "1900-02-28"),
        ("0", "61.000", "1900-03-01"),
        ("0", "+1.462E+3", "1904-01-01"),
        ("0", "2958465", "9999-12-31"),
        ("1", "0", "1904-01-01"),
        ("true", "59", "1904-02-29"),
        ("1", "60", "1904-03-01"),
        ("1", "2957003", "9999-12-31"),
    ],
)
def test_xlsx_integral_dates_use_the_correct_epoch_without_numeric_marking(epoch, serial, expected):
    content = xlsx(
        row(1, text_cell("A1", "data")) + row(2, number_cell("A2", serial, 1)),
        epoch=epoch,
        style_xml=styles(0, 14),
    )
    result = parse_table(content, "a.xlsx").rows[0]
    assert result.values == {"data": expected}
    assert not result.errors
    assert result.numeric_columns == []


@pytest.mark.parametrize("serial", ["60", "60.0", "0", "-1", "1.5", "2958466", "1E999999"])
def test_xlsx_invalid_or_fractional_excel_dates_are_quarantined(serial):
    content = xlsx(
        row(1, text_cell("A1", "data")) + row(2, number_cell("A2", serial, 1)),
        style_xml=styles(0, 14),
    )
    result = parse_table(content, "a.xlsx").rows[0]
    assert result.values["data"] == serial
    assert result.errors
    if serial.startswith("60"):
        assert "1900-02-29" in result.errors[0]


@pytest.mark.parametrize(
    "value,valid",
    [
        ("2024-02-29", True),
        ("1900-02-29", False),
        ("2026-11-10T01:00:00Z", False),
        ("10/11/2026", False),
    ],
)
def test_xlsx_typed_iso_dates_are_validated_without_truncating_times(value, valid):
    content = xlsx(row(1, text_cell("A1", "data")) + row(2, f'<c r="A2" t="d"><v>{value}</v></c>'))
    parsed = parse_table(content, "a.xlsx").rows[0]
    assert bool(parsed.errors) is not valid
    assert parsed.values["data"] == value
    assert not parsed.numeric_columns


@pytest.mark.parametrize("identifier", [9, 10])
def test_xlsx_percent_formats_quarantine_raw_values_without_rescaling(identifier):
    content = xlsx(
        row(1, text_cell("A1", "valor")) + row(2, number_cell("A2", "0.12500", 1)),
        style_xml=styles(0, identifier),
    )
    result = parse_table(content, "a.xlsx").rows[0]
    assert result.values["valor"] == "0.12500"
    assert result.numeric_columns == ["valor"]
    assert "percentual" in result.errors[0]


@pytest.mark.parametrize(
    "code,expected,error",
    [
        ("yyyy-mm-dd", "1900-03-01", False),
        ("[$-409]d/m/yyyy", "1900-03-01", False),
        ("0.00%", "61", True),
        ("[Red][>=0]0.00;0%", "61", True),
        ('0.00"%"', "61", False),
        ("0.00\\%", "61", False),
        ('0.00"USD"', "61", False),
        ("[h]:mm:ss", "61", True),
        ("hh:mm", "61", True),
    ],
)
def test_xlsx_custom_formats_distinguish_literals_dates_time_and_percent(code, expected, error):
    custom = f'<numFmts><numFmt numFmtId="164" formatCode={quoteattr(code)}/></numFmts>'
    content = xlsx(
        row(1, text_cell("A1", "valor")) + row(2, number_cell("A2", "61", 1)),
        style_xml=styles(0, 164, custom=custom),
    )
    result = parse_table(content, "a.xlsx").rows[0]
    assert result.values["valor"] == expected
    assert bool(result.errors) is error


def test_xlsx_column_row_and_base_styles_do_not_hide_percentage_or_date_formats():
    inherited = (
        f'<styleSheet xmlns="{NS}"><cellStyleXfs><xf numFmtId="9"/></cellStyleXfs>'
        '<cellXfs><xf numFmtId="0"/><xf numFmtId="14"/>'
        '<xf xfId="0" applyNumberFormat="0" numFmtId="0"/></cellXfs></styleSheet>'
    )
    content = xlsx(
        row(1, text_cell("A1", "data", 0), text_cell("B1", "percentual", 0))
        + row(2, number_cell("A2", "61"), number_cell("B2", ".5", 2))
        + row(3, number_cell("A3", "61"), attributes='s="1" customFormat="1"'),
        extra='<cols><col min="1" max="1" style="1"/></cols>',
        style_xml=inherited,
    )
    results = parse_table(content, "a.xlsx").rows
    assert results[0].values == {"data": "1900-03-01", "percentual": ".5"}
    assert results[0].numeric_columns == ["percentual"]
    assert "percentual" in results[0].errors[0]
    assert results[1].values["data"] == "1900-03-01"
    assert not results[1].errors


@pytest.mark.parametrize("identifier,code", [(9, "0%"), (14, "yyyy-mm-dd"), (46, "[h]:mm:ss")])
def test_xlsx_conditional_units_and_dates_are_quarantined_without_evaluating_rules(
    identifier, code
):
    style_xml = styles(0).replace(
        "</styleSheet>",
        f'<dxfs><dxf><numFmt numFmtId="{identifier}" formatCode={quoteattr(code)}/>'
        "</dxf></dxfs></styleSheet>",
    )
    content = xlsx(
        row(1, text_cell("A1", "valor"))
        + row(2, number_cell("A2", "0.25"))
        + row(3, number_cell("A3", "1")),
        style_xml=style_xml,
        extra='<conditionalFormatting sqref="A2:A2"><cfRule type="expression" '
        'dxfId="0" priority="1"><formula>1=1</formula></cfRule></conditionalFormatting>',
    )
    rows = parse_table(content, "a.xlsx").rows
    assert rows[0].values["valor"] == "0.25"
    assert any("condicional" in error for error in rows[0].errors)
    assert not rows[1].errors


@pytest.mark.parametrize("value", ["NaN", "Infinity", "1,23", "1_000", "--1", "1e", "１"])
def test_xlsx_invalid_numeric_lexemes_quarantine_without_marking_numeric(value):
    parsed = parse_table(
        xlsx(row(1, text_cell("A1", "v")) + row(2, number_cell("A2", value))), "a.xlsx"
    ).rows[0]
    assert parsed.errors
    assert parsed.values["v"] == value
    assert parsed.numeric_columns == []


@pytest.mark.parametrize(
    "bad_data",
    [
        row(2, number_cell("A2", "1"), number_cell("A2", "2")),
        row(2, number_cell("B2", "1"), number_cell("A2", "2")),
        row(2, number_cell("A3", "1")),
        row(2, number_cell("A0", "1")),
        row(2, number_cell("XFE2", "1")),
        row(1, number_cell("A1", "1")),
    ],
)
def test_xlsx_invalid_or_duplicate_coordinates_reject_the_file(bad_data):
    with pytest.raises(ParseError):
        parse_table(xlsx(row(1, text_cell("A1", "v")) + bad_data), "a.xlsx")


def test_xlsx_shared_string_reference_and_style_indices_are_checked():
    for cell in ['<c r="A2" t="s"><v>9999</v></c>', '<c r="A2" s="9999"><v>1</v></c>']:
        with pytest.raises(ParseError, match="Índice"):
            parse_table(xlsx(row(1, text_cell("A1", "v")) + row(2, cell)), "a.xlsx")


@pytest.mark.parametrize(
    "part,value",
    [
        ("xl/vbaProject.bin", b"synthetic"),
        ("EncryptionInfo", b"synthetic"),
        ("xl/macrosheets/sheet.xml", "<x/>"),
    ],
)
def test_xlsx_macro_and_encryption_parts_are_rejected(part, value):
    parts = package()
    parts[part] = value
    with pytest.raises(ParseError, match="Macros ou criptografia"):
        parse_table(zipped(parts), "renamed.xlsx")


def test_xlsx_renamed_macro_workbook_is_rejected_by_content_type():
    parts = package()
    parts["[Content_Types].xml"] = parts["[Content_Types].xml"].replace(
        MAIN_TYPE, "application/vnd.ms-excel.sheet.macroEnabled.main+xml"
    )
    with pytest.raises(ParseError, match="Macros"):
        parse_table(zipped(parts), "renamed.xlsx")


def test_xlsx_encrypted_zip_flag_and_ole_container_are_rejected():
    content = bytearray(zipped(package()))
    for signature, offset in [(b"PK\x03\x04", 6), (b"PK\x01\x02", 8)]:
        start = content.index(signature) + offset
        flag = struct.unpack_from("<H", content, start)[0]
        struct.pack_into("<H", content, start, flag | 1)
    for encrypted in [bytes(content), bytes.fromhex("d0cf11e0a1b11ae1") + b"EncryptedPackage"]:
        with pytest.raises(ParseError, match="criptografado"):
            parse_table(encrypted, "a.xlsx")


@pytest.mark.parametrize(
    "name",
    [
        "../escape.xml",
        "/absolute.xml",
        "xl/../bad.xml",
        "xl\\bad.xml",
        "xl/bad\x00.xml",
        "xl/WORKBOOK.xml",
    ],
)
def test_xlsx_unsafe_or_case_duplicate_zip_names_are_rejected(name):
    parts = package()
    parts[name] = "<x/>"
    with pytest.raises(ParseError, match="Caminho ZIP|duplicada"):
        parse_table(zipped(parts), "a.xlsx")


def test_xlsx_part_count_boundary_includes_unused_parts():
    parts = package()
    for i in range(400 - len(parts)):
        parts[f"unused/{i}.bin"] = b""
    assert parse_table(zipped(parts), "a.xlsx").rows
    parts["unused/overflow.bin"] = b""
    with pytest.raises(ParseError, match="400 partes"):
        parse_table(zipped(parts), "a.xlsx")


@pytest.mark.parametrize("count,size", [(1, 16 * 1024 * 1024), (3, 6 * 1024 * 1024)])
def test_xlsx_zip_bomb_expanded_budget_includes_unused_binary_parts(count, size):
    parts = package()
    parts.update({f"unused/{i}.bin": b"0" * size for i in range(count)})
    content = zipped(parts)
    assert len(content) < 2 * 1024 * 1024
    with pytest.raises(ParseError, match="16 MiB"):
        parse_table(content, "a.xlsx")


def test_xlsx_exact_expanded_budget_is_allowed():
    parts = package()
    expanded = sum(len(value.encode()) for value in parts.values())
    parts["padding.bin"] = b"0" * (16 * 1024 * 1024 - expanded)
    assert parse_table(zipped(parts), "a.xlsx").rows[0].values == {"valor": "123.45"}


def test_xlsx_forged_expanded_size_and_crc_cannot_hide_a_zip_bomb():
    parts = {"padding.bin": b"0" * (17 * 1024 * 1024), **package()}
    content = bytearray(zipped(parts))
    central = content.index(b"PK\x01\x02")
    # Both headers claim a one-byte member whose CRC matches that one byte.
    # ZipExtFile accepts the truncated prefix; the full deflate stream must not.
    struct.pack_into("<I", content, 22, 1)
    struct.pack_into("<I", content, central + 24, 1)
    struct.pack_into("<I", content, 14, zlib.crc32(b"0"))
    struct.pack_into("<I", content, central + 16, zlib.crc32(b"0"))
    with zipfile.ZipFile(BytesIO(content)) as archive:
        assert archive.read("padding.bin") == b"0"
    with pytest.raises(ParseError, match="XLSX/ZIP inválido"):
        parse_table(bytes(content), "a.xlsx")


def test_xlsx_malformed_truncated_or_crc_invalid_zip_is_rejected():
    content = zipped(package(), zipfile.ZIP_STORED)
    corrupt = content.replace(b"123.45", b"999.99", 1)
    for invalid in [b"not zip", content[:-30], corrupt]:
        with pytest.raises(ParseError, match="XLSX/ZIP"):
            parse_table(invalid, "a.xlsx")


@pytest.mark.parametrize(
    "xml",
    [
        '<!DOCTYPE x [<!ENTITY p SYSTEM "file:///no-read">]><x>&p;</x>',
        '<!DOCTYPE x [<!ENTITY a "boom"><!ENTITY b "&a;&a;">]><x>&b;</x>',
        '<!DOCTYPE x SYSTEM "https://example.invalid/no-fetch"><x/>',
        "<x>",
    ],
)
def test_xlsx_unsafe_or_malformed_xml_is_rejected_even_in_unused_parts(xml):
    parts = package()
    parts["unused.xml"] = xml
    with pytest.raises(ParseError, match="XML inválido ou inseguro"):
        parse_table(zipped(parts), "a.xlsx")


def test_xlsx_utf16_dtd_is_also_blocked():
    parts = package()
    parts["unused.xml"] = '<!DOCTYPE x [<!ENTITY a "boom">]><x>&a;</x>'.encode("utf-16")
    with pytest.raises(ParseError, match="XML inválido ou inseguro"):
        parse_table(zipped(parts), "a.xlsx")


@pytest.mark.parametrize("encoding", ["not-a-codec", "UTF-32"])
def test_xlsx_unsupported_xml_encoding_raises_public_parse_error(encoding):
    parts = package()
    parts["unused.xml"] = f'<?xml version="1.0" encoding="{encoding}"?><x/>'
    with pytest.raises(ParseError, match="XML inválido"):
        parse_table(zipped(parts), "a.xlsx")


@pytest.mark.parametrize("xml", ["<x>" * 65 + "</x>" * 65, "<x>" + "<v/>" * 200_000 + "</x>"])
def test_xlsx_xml_depth_and_total_nodes_are_bounded(xml):
    parts = package()
    parts["unused.xml"] = xml
    with pytest.raises(ParseError, match="complexidade XML"):
        parse_table(zipped(parts), "a.xlsx")


def test_xlsx_metadata_and_string_lengths_are_bounded():
    parts = package()
    parts["unused.xml"] = "<x><!--" + "x" * (1024 * 1024) + "--></x>"
    with pytest.raises(ParseError, match="Metadados XLSX"):
        parse_table(zipped(parts), "a.xlsx")
    assert parse_table(
        xlsx(row(1, text_cell("A1", "h" * 200)) + row(2, text_cell("A2", "v" * 2000))), "a.xlsx"
    ).rows
    for rows in [
        row(1, text_cell("A1", "h" * 201)),
        row(1, text_cell("A1", "h")) + row(2, text_cell("A2", "v" * 2001)),
        row(1, text_cell("A1", "h"))
        + row(
            2,
            '<c r="A2" t="inlineStr"><is>'
            "<r><t>" + "v" * 1001 + "</t></r><r><t>" + "v" * 1000 + "</t></r></is></c>",
        ),
    ]:
        with pytest.raises(ParseError, match="caracteres"):
            parse_table(xlsx(rows), "a.xlsx")


@pytest.mark.parametrize("text", ["\x00", "_x0000_", "_xD800_"])
def test_xlsx_nul_and_invalid_surrogates_cannot_reach_postgresql(text):
    with pytest.raises(ParseError):
        parse_table(
            xlsx(row(1, text_cell("A1", "valor")) + row(2, text_cell("A2", text))), "a.xlsx"
        )


def test_xlsx_plain_string_escapes_cannot_hide_nul():
    content = xlsx(
        row(1, text_cell("A1", "valor")) + row(2, '<c r="A2" t="str"><v>_x0000_</v></c>')
    )
    with pytest.raises(ParseError, match="NUL"):
        parse_table(content, "a.xlsx")


def test_xlsx_urls_and_hyperlink_external_relationships_are_inert(monkeypatch):
    import urllib.request

    def no_network(*args, **kwargs):
        pytest.fail("The parser must never fetch a URL")

    monkeypatch.setattr(urllib.request, "urlopen", no_network)
    parts = package(
        {
            "Dados": worksheet(
                row(1, text_cell("A1", "url"))
                + row(2, text_cell("A2", "https://example.invalid/data")),
                f'<hyperlinks xmlns:r="{REL}"><hyperlink ref="A2" r:id="link"/></hyperlinks>',
            )
        }
    )
    parts["xl/worksheets/_rels/sheet1.xml.rels"] = (
        f'<Relationships xmlns="{PKG}"><Relationship Id="link" Type="{REL}/hyperlink" '
        'TargetMode="External" Target="https://example.invalid/no-fetch"/></Relationships>'
    )
    result = parse_table(zipped(parts), "a.xlsx")
    assert result.rows[0].values == {"url": "https://example.invalid/data"}
    assert not result.rows[0].errors


@pytest.mark.parametrize(
    "target",
    [
        "../../../escape.xml",
        "https://example.invalid/sheet.xml",
        "//example.invalid/sheet.xml",
        "%2e%2e/%2e%2e/escape.xml",
    ],
)
def test_xlsx_worksheet_relationship_cannot_escape_package(target):
    parts = package()
    parts["xl/_rels/workbook.xml.rels"] = parts["xl/_rels/workbook.xml.rels"].replace(
        'Target="worksheets/sheet1.xml"', f"Target={quoteattr(target)}"
    )
    with pytest.raises(ParseError, match="Destino XLSX"):
        parse_table(zipped(parts), "a.xlsx")


def test_xlsx_external_worksheet_is_rejected_without_fetching():
    parts = package()
    parts["xl/_rels/workbook.xml.rels"] = parts["xl/_rels/workbook.xml.rels"].replace(
        'Target="worksheets/sheet1.xml"', 'TargetMode="External" Target="https://example.invalid/a"'
    )
    with pytest.raises(ParseError, match="externa"):
        parse_table(zipped(parts), "a.xlsx")


def test_xlsx_absolute_package_relationship_targets_are_supported():
    parts = package()
    parts["xl/_rels/workbook.xml.rels"] = parts["xl/_rels/workbook.xml.rels"].replace(
        'Target="worksheets/sheet1.xml"', 'Target="/xl/worksheets/sheet1.xml"'
    )
    assert parse_table(zipped(parts), "a.xlsx").rows[0].values == {"valor": "123.45"}
