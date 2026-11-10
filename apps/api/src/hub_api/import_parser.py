"""Bounded table ingestion; no locale inference, float conversion or workbook execution.

The first nonempty record is the header. CSV row numbers are physical starting
lines (including quoted newlines); XLSX numbers are worksheet row coordinates.
Blank cells are None, other text retains whitespace, and headers are stripped.
Consumers MUST quarantine rows with errors. Formula caches are discarded.
``numeric_columns`` identifies raw XML numbers, never CSV/text cells or dates
converted to ISO. Business validation and locale conversion belong to the caller.
"""

from __future__ import annotations

import posixpath
import re
import zipfile
import zlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import unquote, urlsplit
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import ParseError as XMLParseError

from defusedxml import ElementTree as SafeXML
from defusedxml.common import DefusedXmlException

MAX_UPLOAD_BYTES = 2 * 1024 * 1024
MAX_ROWS = 500
MAX_COLUMNS = 40
MAX_EXPANDED_BYTES = 16 * 1024 * 1024
MAX_PARTS = 400
MAX_CELL_CHARS = 2000
MAX_HEADER_CHARS = 200
_MAX_METADATA_BYTES = 1024 * 1024
_MAX_XML_NODES = 200_000
_MAX_XML_DEPTH = 64
_MAX_STYLES = 4096
_MAX_SHARED_STRINGS = (MAX_ROWS + 1) * MAX_COLUMNS
_MAX_SHEETS = 50
_MAX_RANGES = 2000
_EXCEL_MAX_ROW = 1_048_576
_EXCEL_MAX_COL = 16_384
_MAIN_NS = (
    "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "http://purl.oclc.org/ooxml/spreadsheetml/main",
)
_DOC_REL_NS = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "http://purl.oclc.org/ooxml/officeDocument/relationships",
)
_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_CONTENT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
_WORKBOOK_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
_NUMERIC = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
_COORDINATE = re.compile(r"([A-Z]{1,3})([1-9][0-9]{0,6})\Z")
_ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")
_ESCAPE = re.compile(r"_x([0-9a-fA-F]{4})_")
_DATE_FORMATS = {14, 15, 16, 17, 22, *range(27, 32), *range(34, 37), *range(50, 59)}
_TIME_FORMATS = {18, 19, 20, 21, 32, 33, 45, 46, 47}
_NUMBER_FORMATS = {0, *range(1, 9), 11, 12, 13, *range(37, 45), 48, 49}


class ParseError(ValueError):
    """An unsafe, malformed or oversized file cannot produce a table."""


@dataclass
class ParsedRow:
    number: int
    values: dict[str, str | None]
    errors: list[str]
    numeric_columns: list[str] = field(default_factory=list)


@dataclass
class ParsedTable:
    headers: list[str]
    rows: list[ParsedRow]
    sheet: str | None


def _text(value: str | None, limit: int = MAX_CELL_CHARS) -> str | None:
    if value is None:
        return None
    if "\x00" in value:
        raise ParseError("Texto contém NUL, não permitido.")
    if len(value) > limit:
        raise ParseError(f"Texto excede {limit} caracteres.")
    return value if value.strip() else None


def _headers(values: list[str | None]) -> list[str]:
    if not values or len(values) > MAX_COLUMNS:
        raise ParseError("Limite de 40 colunas excedido.")
    result = []
    for value in values:
        if value is None or not value.strip():
            raise ParseError("Cabeçalho vazio.")
        _text(value, MAX_HEADER_CHARS)
        result.append(value.strip())
    if len({value.casefold() for value in result}) != len(result):
        raise ParseError("Cabeçalhos duplicados.")
    return result


def _append_row(rows: list[ParsedRow], row: ParsedRow) -> None:
    if len(rows) >= MAX_ROWS:
        raise ParseError("Limite de 500 linhas de dados excedido.")
    rows.append(row)


def _csv_records(text: str, delimiter: str) -> Iterator[tuple[int, list[str | None]]]:
    # csv.reader(strict=True) still accepts quotes inside unquoted fields.
    # This four-state lexer also rejects that ambiguity without global settings.
    state = "start"
    fields: list[str | None] = []
    chars: list[str] = []
    line = start_line = 1
    index = 0
    while index < len(text):
        char = text[index]
        index += 1
        newline = char in "\r\n"
        if char == "\r" and index < len(text) and text[index] == "\n":
            char = "\r\n"
            index += 1
        if newline:
            line += 1
        if state == "quoted":
            if char == '"':
                state = "closed"
            else:
                chars.extend(char)
        elif char == delimiter or newline:
            fields.append(_text("".join(chars)))
            chars = []
            state = "start"
            if newline:
                yield start_line, fields
                fields = []
                start_line = line
            elif len(fields) >= MAX_COLUMNS:
                raise ParseError("Limite de 40 colunas excedido.")
        elif char == '"' and state in {"start", "closed"}:
            if state == "closed":
                chars.append('"')
            state = "quoted"
        elif char == '"' or state == "closed":
            raise ParseError(f"CSV inválido: aspas na linha {line}.")
        else:
            chars.append(char)
            state = "unquoted"
        if len(chars) > MAX_CELL_CHARS:
            raise ParseError("Texto excede 2000 caracteres.")
    if state == "quoted":
        raise ParseError("CSV inválido: aspas não fechadas.")
    if fields or chars or state != "start":
        fields.append(_text("".join(chars)))
        yield start_line, fields


def _parse_csv(content: bytes, delimiter: str, encoding: str) -> ParsedTable:
    if delimiter not in {",", ";", "\t"}:
        raise ParseError("Separador deve ser vírgula, ponto e vírgula ou tabulação.")
    encodings = {
        "utf-8": "utf-8-sig",
        "utf8": "utf-8-sig",
        "utf-8-sig": "utf-8-sig",
        "cp1252": "cp1252",
        "windows-1252": "cp1252",
    }
    codec = encodings.get(encoding.lower().replace("_", "-"))
    if codec is None:
        raise ParseError("Codificação deve ser UTF-8 ou cp1252.")
    try:
        text = content.decode(codec, errors="strict")
    except UnicodeDecodeError as exc:
        raise ParseError("Codificação inválida; use UTF-8 ou selecione cp1252.") from exc
    if "\x00" in text:
        raise ParseError("Texto contém NUL, não permitido.")
    headers: list[str] = []
    rows: list[ParsedRow] = []
    for number, values in _csv_records(text, delimiter):
        if not any(value is not None for value in values):
            continue
        if not headers:
            headers = _headers(values)
            continue
        errors = []
        if len(values) != len(headers):
            errors.append(f"Esperadas {len(headers)} colunas; recebidas {len(values)}.")
        mapped = {
            header: values[i] if i < len(values) else None for i, header in enumerate(headers)
        }
        _append_row(rows, ParsedRow(number, mapped, errors))
    if not headers:
        raise ParseError("Arquivo sem cabeçalho.")
    return ParsedTable(headers, rows, None)


def _xml(data: bytes, remaining_nodes: int) -> tuple[Element, int]:
    depth = nodes = 0
    root = None
    try:
        for event, element in SafeXML.iterparse(
            BytesIO(data),
            events=("start", "end"),
            forbid_dtd=True,
            forbid_entities=True,
            forbid_external=True,
        ):
            if event == "start":
                nodes += 1
                depth += 1
                if nodes > remaining_nodes or depth > _MAX_XML_DEPTH:
                    raise ParseError("Limite de complexidade XML excedido.")
                if root is None:
                    root = element
                _text(element.tag)
                if len(element.attrib) > 64:
                    raise ParseError("Metadados XML excedem o limite.")
                for key, value in element.attrib.items():
                    _text(key)
                    _text(value)
            else:
                _text(element.text)
                _text(element.tail)
                depth -= 1
    except ParseError:
        raise
    except (XMLParseError, DefusedXmlException, LookupError, ValueError) as exc:
        raise ParseError("XML inválido ou inseguro no XLSX.") from exc
    if root is None:
        raise ParseError("XML vazio no XLSX.")
    return root, nodes


def _member_data(content: bytes, info: zipfile.ZipInfo, remaining: int) -> bytes:
    # ZipExtFile truncates output at the *declared* size. Inflate independently
    # with a hard output cap to detect dishonest sizes, even with a forged CRC.
    offset = info.header_offset
    if not 0 <= offset <= len(content) - 30:
        raise zipfile.BadZipFile("Invalid local header")
    name_size = int.from_bytes(content[offset + 26 : offset + 28], "little")
    extra_size = int.from_bytes(content[offset + 28 : offset + 30], "little")
    start = offset + 30 + name_size + extra_size
    end = start + info.compress_size
    if end > len(content):
        raise zipfile.BadZipFile("Truncated member")
    compressed = content[start:end]
    if info.compress_type == zipfile.ZIP_DEFLATED:
        inflater = zlib.decompressobj(-zlib.MAX_WBITS)
        data = inflater.decompress(compressed, min(info.file_size, remaining) + 1)
        if not inflater.eof or inflater.unused_data:
            raise zipfile.BadZipFile("Invalid deflate size or stream")
    else:
        data = compressed
    if len(data) > remaining:
        raise ParseError("XLSX excede 16 MiB descompactados.")
    if len(data) != info.file_size or zlib.crc32(data) != info.CRC:
        raise zipfile.BadZipFile("Invalid member size or CRC")
    return data


def _package(content: bytes) -> dict[str, Element]:
    """Read every member with a hard budget, including unused sheets/binaries.

    Members are never extracted. ZipFile checks local headers and overlaps;
    actual inflation sizes and CRCs are checked separately. Stored/deflated only.
    """
    parts = {}
    names: set[str] = set()
    expanded = nodes = 0
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_PARTS:
                raise ParseError("XLSX excede 400 partes ZIP.")
            if sum(info.file_size for info in infos) > MAX_EXPANDED_BYTES:
                raise ParseError("XLSX excede 16 MiB descompactados.")
            if len(archive.comment) > MAX_CELL_CHARS:
                raise ParseError("Metadados ZIP excedem o limite.")
            for info in infos:
                name = info.filename
                if (
                    len(name) > 512
                    or info.orig_filename != name
                    or "\\" in name
                    or name.startswith("/")
                    or ":" in name
                    or any(ord(c) < 32 for c in name)
                    or any(p in {"", ".", ".."} for p in name.rstrip("/").split("/"))
                ):
                    raise ParseError("Caminho ZIP inválido.")
                if name.casefold() in names:
                    raise ParseError("Parte ZIP duplicada.")
                names.add(name.casefold())
                if any(
                    token in name.lower()
                    for token in ("vba", "macrosheet", "encryptedpackage", "encryptioninfo")
                ):
                    raise ParseError("Macros ou criptografia não são permitidas.")
                if info.flag_bits & 0x41:
                    raise ParseError("XLSX criptografado não é permitido.")
                if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
                    raise ParseError("Compressão ZIP não suportada.")
                with archive.open(info):
                    data = _member_data(content, info, MAX_EXPANDED_BYTES - expanded)
                expanded += len(data)
                if expanded > MAX_EXPANDED_BYTES:
                    raise ParseError("XLSX excede 16 MiB descompactados.")
                if len(data) != info.file_size:
                    raise ParseError("Parte ZIP truncada.")
                if name.lower().endswith((".xml", ".rels")):
                    root, count = _xml(data, _MAX_XML_NODES - nodes)
                    nodes += count
                    if len(data) > _MAX_METADATA_BYTES and root.tag not in {
                        f"{{{ns}}}{tag}" for ns in _MAIN_NS for tag in ("worksheet", "sst")
                    }:
                        raise ParseError("Metadados XLSX excedem o limite.")
                    for element in root.iter():
                        kind = element.get("ContentType", "") + element.get("Type", "")
                        if any(
                            token in kind.lower()
                            for token in ("macroenabled", "macrosheet", "vbaproject", "vbadata")
                        ):
                            raise ParseError("Macros não são permitidas.")
                    parts[name] = root
    except ParseError:
        raise
    except (
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
        OSError,
        EOFError,
        RuntimeError,
        NotImplementedError,
        zlib.error,
        ValueError,
    ) as exc:
        raise ParseError("Arquivo XLSX/ZIP inválido ou criptografado.") from exc
    return parts


def _required(parts: dict[str, Element], path: str) -> Element:
    if path not in parts:
        raise ParseError("Parte obrigatória ausente no XLSX.")
    return parts[path]


def _namespace(root: Element, tag: str) -> str:
    for namespace in _MAIN_NS:
        if root.tag == f"{{{namespace}}}{tag}":
            return f"{{{namespace}}}"
    raise ParseError("Estrutura XML incompatível com XLSX.")


def _single(root: Element, tag: str) -> Element | None:
    matches = root.findall(tag)
    if len(matches) > 1:
        raise ParseError("Elemento XML duplicado.")
    return matches[0] if matches else None


def _uint(value: str | None, maximum: int, *, minimum: int = 0) -> int:
    if value is None or not re.fullmatch(r"[0-9]{1,10}", value):
        raise ParseError("Índice inválido no XLSX.")
    number = int(value)
    if not minimum <= number <= maximum:
        raise ParseError("Índice fora do limite no XLSX.")
    return number


def _boolean(value: str) -> bool:
    if value not in {"0", "1", "true", "false"}:
        raise ParseError("Metadado booleano inválido no XLSX.")
    return value in {"1", "true"}


def _relationships(parts: dict[str, Element], source: str) -> dict[str, Element]:
    path = posixpath.join(posixpath.dirname(source), "_rels", posixpath.basename(source) + ".rels")
    root = _required(parts, path)
    if root.tag != f"{{{_REL_NS}}}Relationships":
        raise ParseError("Relações XLSX inválidas.")
    result = {}
    for relation in root:
        identifier = relation.get("Id", "")
        if (
            relation.tag != f"{{{_REL_NS}}}Relationship"
            or not identifier
            or len(identifier) > 200
            or identifier in result
            or not relation.get("Type")
            or not relation.get("Target")
            or relation.get("TargetMode", "Internal") not in {"Internal", "External"}
        ):
            raise ParseError("Relação XLSX inválida ou duplicada.")
        result[identifier] = relation
    return result


def _is_relation(relation: Element, kind: str) -> bool:
    return relation.get("Type") in {f"{ns}/{kind}" for ns in _DOC_REL_NS}


def _target(source: str, relation: Element) -> str:
    if relation.get("TargetMode") == "External":
        raise ParseError("Parte XLSX externa não é permitida.")
    try:
        target = unquote(relation.get("Target", ""), errors="strict")
        parsed = urlsplit(target)
    except (UnicodeError, ValueError) as exc:
        raise ParseError("Destino XLSX inválido.") from exc
    if (
        not target
        or parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or "\\" in target
        or any(ord(c) < 32 for c in target)
    ):
        raise ParseError("Destino XLSX inválido.")
    path = posixpath.normpath(
        posixpath.join(posixpath.dirname(source), target)
        if not target.startswith("/")
        else target[1:]
    )
    if path in {".", ".."} or path.startswith("../"):
        raise ParseError("Destino XLSX fora do pacote.")
    return path


def _related_part(
    parts: dict[str, Element], relations: dict[str, Element], source: str, kind: str
) -> Element | None:
    matches = [r for r in relations.values() if _is_relation(r, kind)]
    if len(matches) > 1:
        raise ParseError("Parte XLSX ambígua.")
    return _required(parts, _target(source, matches[0])) if matches else None


def _unescape(value: str) -> str | None:
    value = _ESCAPE.sub(lambda match: chr(int(match[1], 16)), value)
    try:
        value = value.encode("utf-16-le", errors="surrogatepass").decode("utf-16-le")
    except UnicodeError as exc:
        raise ParseError("Texto Unicode inválido no XLSX.") from exc
    return _text(value)


def _string(element: Element, ns: str) -> str | None:
    # Phonetic annotations (rPh) do not belong to the displayed cell value.
    pieces = []
    for child in element:
        if child.tag == ns + "t":
            pieces.append(child.text or "")
        elif child.tag == ns + "r":
            pieces.extend(node.text or "" for node in child.findall(ns + "t"))
    return _unescape("".join(pieces))


def _shared_strings(root: Element | None) -> list[str | None]:
    if root is None:
        return []
    ns = _namespace(root, "sst")
    if len(root) > _MAX_SHARED_STRINGS:
        raise ParseError("Limite de textos compartilhados excedido.")
    result = []
    for child in root:
        if child.tag != ns + "si":
            raise ParseError("Tabela de textos XLSX inválida.")
        result.append(_string(child, ns))
    return result


def _format_kind(identifier: int, custom: dict[int, str]) -> str:
    if identifier not in custom:
        if identifier in {9, 10}:
            return "percent"
        if identifier in _DATE_FORMATS:
            return "date"
        if identifier in _TIME_FORMATS:
            return "time"
        return "number" if identifier in _NUMBER_FORMATS else "unsupported"
    code = custom[identifier]
    # Discard literal strings, escapes, padding, locale, color and conditions.
    tokens = []
    index = 0
    while index < len(code):
        char = code[index]
        index += 1
        if char == '"':
            end = code.find('"', index)
            if end < 0:
                raise ParseError("Formato numérico XLSX inválido.")
            index = end + 1
        elif char in "\\_*":
            index += 1
        elif char == "[":
            end = code.find("]", index)
            if end < 0:
                raise ParseError("Formato numérico XLSX inválido.")
            bracket = code[index:end].lower()
            if bracket in {"h", "hh", "m", "mm", "s", "ss"}:
                tokens.append("h")  # elapsed time, including [m]
            index = end + 1
        else:
            tokens.append(char.lower())
    code = "".join(tokens)
    if "%" in code:
        return "percent"
    if any(char in code for char in "yd") or ("m" in code and not any(c in code for c in "hs")):
        return "date"
    return "time" if any(char in code for char in "hs") else "number"


def _styles(root: Element | None) -> list[str]:
    if root is None:
        return ["number"]
    ns = _namespace(root, "styleSheet")
    custom: dict[int, str] = {}
    formats = _single(root, ns + "numFmts")
    if formats is not None:
        if len(formats) > _MAX_STYLES:
            raise ParseError("Limite de formatos XLSX excedido.")
        for item in formats:
            identifier = _uint(item.get("numFmtId"), 65535)
            code = item.get("formatCode")
            if item.tag != ns + "numFmt" or identifier in custom or not code:
                raise ParseError("Formato numérico XLSX inválido ou duplicado.")
            custom[identifier] = code
    bases = _single(root, ns + "cellStyleXfs")
    base_formats = []
    if bases is not None:
        if len(bases) > _MAX_STYLES:
            raise ParseError("Limite de estilos XLSX excedido.")
        base_formats = [_uint(item.get("numFmtId", "0"), 65535) for item in bases]
    cell_styles = _single(root, ns + "cellXfs")
    if cell_styles is None:
        return ["number"]
    if not 1 <= len(cell_styles) <= _MAX_STYLES:
        raise ParseError("Limite de estilos XLSX excedido.")
    result = []
    for item in cell_styles:
        if item.tag != ns + "xf":
            raise ParseError("Estilo XLSX inválido.")
        identifier = _uint(item.get("numFmtId", "0"), 65535)
        if "xfId" in item.attrib:
            base = base_formats[_uint(item.get("xfId"), len(base_formats) - 1)]
            if "numFmtId" not in item.attrib or not _boolean(item.get("applyNumberFormat", "1")):
                identifier = base
        result.append(_format_kind(identifier, custom))
    return result


def _conditional_ranges(root: Element, styles: Element | None) -> list[tuple[int, int, int, int]]:
    """Conditional number formats cannot be resolved without evaluating rules."""
    kinds = []
    if styles is not None:
        style_ns = _namespace(styles, "styleSheet")
        differential = _single(styles, style_ns + "dxfs")
        if differential is not None:
            if len(differential) > _MAX_STYLES:
                raise ParseError("Limite de estilos XLSX excedido.")
            for item in differential:
                number_format = _single(item, style_ns + "numFmt")
                kind = "number"
                if number_format is not None:
                    identifier = _uint(number_format.get("numFmtId", "0"), 65535)
                    code = number_format.get("formatCode")
                    kind = _format_kind(identifier, {identifier: code} if code else {})
                kinds.append(kind)
    ns = _namespace(root, "worksheet")
    ranges = []
    for conditional in root.findall(ns + "conditionalFormatting"):
        unsafe = False
        for rule in conditional.findall(ns + "cfRule"):
            if "dxfId" in rule.attrib:
                index = _uint(rule.get("dxfId"), len(kinds) - 1)
                unsafe |= kinds[index] != "number"
        if unsafe:
            for reference in conditional.get("sqref", "").split():
                ranges.append(_range(reference))
                if len(ranges) > _MAX_RANGES:
                    raise ParseError("Limite de intervalos condicionais excedido.")
            if not conditional.get("sqref", "").strip():
                raise ParseError("Intervalo condicional ausente.")
    return ranges


def _coordinate(value: str) -> tuple[int, int]:
    match = _COORDINATE.fullmatch(value)
    if not match:
        raise ParseError("Coordenada XLSX inválida.")
    column = 0
    for char in match[1]:
        column = column * 26 + ord(char) - ord("A") + 1
    row = int(match[2])
    if column > _EXCEL_MAX_COL or row > _EXCEL_MAX_ROW:
        raise ParseError("Coordenada XLSX fora do limite.")
    return row, column


def _range(value: str) -> tuple[int, int, int, int]:
    ends = value.split(":")
    if len(ends) not in {1, 2}:
        raise ParseError("Intervalo XLSX inválido.")
    first = _coordinate(ends[0])
    last = _coordinate(ends[-1])
    if first[0] > last[0] or first[1] > last[1]:
        raise ParseError("Intervalo XLSX invertido.")
    return first[0], first[1], last[0], last[1]


def _touches(ranges: list[tuple[int, int, int, int]], number: int, width: int) -> bool:
    return any(r1 <= number <= r2 and c1 <= width for r1, c1, r2, _ in ranges)


def _excel_date(value: Decimal, epoch_1904: bool) -> str:
    minimum, maximum = (0, 2_957_003) if epoch_1904 else (1, 2_958_465)
    if value < minimum or value > maximum or value != value.to_integral_value():
        raise ValueError("Data Excel deve ser integral e válida, sem horário.")
    serial = int(value)
    if not epoch_1904 and serial == 60:
        raise ValueError("Data fictícia 1900-02-29 não é permitida.")
    base = date(1904, 1, 1) if epoch_1904 else date(1899, 12, 31)
    if not epoch_1904 and serial > 60:
        serial -= 1
    return (base + timedelta(days=serial)).isoformat()


@dataclass
class _Cell:
    value: str | None
    errors: list[str] = field(default_factory=list)
    numeric: bool = False


def _cell(
    element: Element, ns: str, strings: list[str | None], kind: str, epoch_1904: bool
) -> _Cell:
    if _single(element, ns + "f") is not None:
        return _Cell(None, ["Fórmula não permitida."])
    value_element = _single(element, ns + "v")
    inline = _single(element, ns + "is")
    raw = _text(value_element.text) if value_element is not None else None
    cell_type = element.get("t", "n")
    if inline is not None and (cell_type != "inlineStr" or value_element is not None):
        raise ParseError("Conteúdo de célula XLSX ambíguo.")
    result = _Cell(raw)
    if cell_type == "inlineStr":
        result.value = _string(inline, ns) if inline is not None else None
    elif cell_type == "s":
        if raw is not None:
            result.value = strings[_uint(raw, len(strings) - 1)]
    elif cell_type == "str" and raw is not None:
        result.value = _unescape(raw)
    elif cell_type == "e":
        result.errors.append("Célula contém erro do Excel.")
    elif cell_type not in {"n", "str", "b", "d"}:
        result.errors.append("Tipo de célula não suportado.")
    if result.value is None and not result.errors:
        return result  # styled empty cells do not create data rows
    if kind == "percent":
        result.errors.append("Formato percentual exige unidade explícita.")
    elif kind == "time":
        result.errors.append("Formato de horário não suportado.")
    elif kind == "unsupported":
        result.errors.append("Formato numérico não suportado.")
    if cell_type == "n" and raw is not None:
        try:
            if not _NUMERIC.fullmatch(raw.strip()):
                raise InvalidOperation
            numeric = Decimal(raw)
            if not numeric.is_finite():
                raise InvalidOperation
            result.numeric = True
            if kind == "date":
                result.value = _excel_date(numeric, epoch_1904)
                result.numeric = False
        except InvalidOperation:
            result.errors.append("Número XML inválido.")
        except ValueError as exc:
            result.errors.append(str(exc))
    elif cell_type == "b" and raw not in {"0", "1"}:
        result.errors.append("Booleano XLSX inválido.")
    elif (cell_type == "d" or kind == "date") and result.value is not None:
        try:
            if not _ISO_DATE.fullmatch(result.value):
                raise ValueError
            date.fromisoformat(result.value)
        except ValueError:
            result.errors.append("Data deve ser ISO (AAAA-MM-DD).")
    return result


def _worksheet(
    root: Element,
    sheet: str,
    strings: list[str | None],
    styles: list[str],
    epoch_1904: bool,
    conditional_ranges: list[tuple[int, int, int, int]],
) -> ParsedTable:
    ns = _namespace(root, "worksheet")
    merges = []
    merge_cells = _single(root, ns + "mergeCells")
    if merge_cells is not None:
        if len(merge_cells) > _MAX_RANGES:
            raise ParseError("Limite de mesclagens excedido.")
        merges = [_range(item.get("ref", "")) for item in merge_cells]
    formula_ranges = []
    for formula in root.iter(ns + "f"):
        if formula.get("ref"):
            formula_ranges.append(_range(formula.get("ref", "")))
            if len(formula_ranges) > _MAX_RANGES:
                raise ParseError("Limite de intervalos de fórmula excedido.")
    column_styles: dict[int, str] = {}
    columns = _single(root, ns + "cols")
    if columns is not None:
        for column in columns:
            first = _uint(column.get("min"), _EXCEL_MAX_COL, minimum=1)
            last = _uint(column.get("max"), _EXCEL_MAX_COL, minimum=first)
            kind = styles[_uint(column.get("style", "0"), len(styles) - 1)]
            for index in range(first, min(last, MAX_COLUMNS) + 1):
                column_styles[index] = kind
    data = _single(root, ns + "sheetData")
    if data is None:
        raise ParseError("Aba sem cabeçalho.")
    headers: list[str] = []
    rows: list[ParsedRow] = []
    previous_row = 0
    for row in data:
        if row.tag != ns + "row":
            raise ParseError("Estrutura de linhas XLSX inválida.")
        number = _uint(row.get("r", str(previous_row + 1)), _EXCEL_MAX_ROW, minimum=1)
        if number <= previous_row:
            raise ParseError("Linhas XLSX duplicadas ou fora de ordem.")
        previous_row = number
        row_style = None
        if _boolean(row.get("customFormat", "0")):
            row_style = styles[_uint(row.get("s", "0"), len(styles) - 1)]
        cells = {}
        previous_column = 0
        for element in row:
            if element.tag != ns + "c":
                raise ParseError("Estrutura de células XLSX inválida.")
            cell_row, column = (
                _coordinate(element.attrib["r"])
                if "r" in element.attrib
                else (number, previous_column + 1)
            )
            if cell_row != number or column <= previous_column or column > _EXCEL_MAX_COL:
                raise ParseError("Células XLSX duplicadas ou fora de ordem.")
            previous_column = column
            kind = row_style or column_styles.get(column, styles[0])
            if "s" in element.attrib:
                kind = styles[_uint(element.get("s"), len(styles) - 1)]
            cell = _cell(element, ns, strings, kind, epoch_1904)
            if cell.value is not None or cell.errors:
                if column > MAX_COLUMNS:
                    raise ParseError("Limite de 40 colunas excedido.")
                cells[column] = cell
        if not cells:
            continue
        width = max(cells)
        errors = [
            f"Coluna {column}: {error}" for column, cell in cells.items() for error in cell.errors
        ]
        if _touches(merges, number, max(width, len(headers))):
            errors.append("Células mescladas na linha.")
        if _touches(formula_ranges, number, max(width, len(headers))):
            errors.append("Linha pertence a intervalo de fórmula.")
        if _touches(conditional_ranges, number, max(width, len(headers))):
            errors.append("Formatação numérica condicional exige revisão.")
        if not headers:
            if errors:
                raise ParseError("Cabeçalho contém células inválidas, fórmulas ou mesclagens.")
            headers = _headers(
                [cells[i].value if i in cells else None for i in range(1, width + 1)]
            )
            continue
        if width > len(headers):
            errors.append(f"Esperadas {len(headers)} colunas; recebidas {width}.")
        values = {
            header: cells[i].value if i in cells else None for i, header in enumerate(headers, 1)
        }
        numeric_columns = [
            header for i, header in enumerate(headers, 1) if i in cells and cells[i].numeric
        ]
        _append_row(rows, ParsedRow(number, values, errors, numeric_columns))
    if not headers:
        raise ParseError("Aba sem cabeçalho.")
    return ParsedTable(headers, rows, sheet)


def _parse_xlsx(content: bytes, sheet: str | None) -> ParsedTable:
    parts = _package(content)
    manifest = _required(parts, "[Content_Types].xml")
    if manifest.tag != f"{{{_CONTENT_NS}}}Types":
        raise ParseError("Tipos de conteúdo XLSX inválidos.")
    roots = [r for r in _relationships(parts, "").values() if _is_relation(r, "officeDocument")]
    if len(roots) != 1:
        raise ParseError("Pasta de trabalho XLSX ausente ou ambígua.")
    path = _target("", roots[0])
    if not any(
        item.get("PartName") == "/" + path and item.get("ContentType") == _WORKBOOK_TYPE
        for item in manifest
    ):
        raise ParseError("Tipo de pasta de trabalho não suportado.")
    workbook = _required(parts, path)
    ns = _namespace(workbook, "workbook")
    properties = _single(workbook, ns + "workbookPr")
    epoch_1904 = _boolean(properties.get("date1904", "0")) if properties is not None else False
    relations = _relationships(parts, path)
    sheets = _single(workbook, ns + "sheets")
    if sheets is None or not 1 <= len(sheets) <= _MAX_SHEETS:
        raise ParseError("XLSX deve conter entre 1 e 50 abas.")
    available = {}
    identifiers: set[int] = set()
    for item in sheets:
        name = item.get("name", "")
        identifier = _uint(item.get("sheetId"), 2**31 - 1, minimum=1)
        if (
            item.tag != ns + "sheet"
            or not name.strip()
            or len(name) > 31
            or any(c in name for c in "[]:*?/\\")
            or any(ord(c) < 32 for c in name)
            or name.casefold() in {key.casefold() for key in available}
            or identifier in identifiers
        ):
            raise ParseError("Nome ou identificação de aba inválido ou duplicado.")
        identifiers.add(identifier)
        rel_ids = [
            item.get(f"{{{rel_ns}}}id")
            for rel_ns in _DOC_REL_NS
            if item.get(f"{{{rel_ns}}}id") is not None
        ]
        if len(rel_ids) != 1 or rel_ids[0] not in relations:
            raise ParseError("Relação da aba ausente ou ambígua.")
        available[name] = relations[rel_ids[0]]
    if sheet is None:
        if len(available) != 1:
            raise ParseError("Escolha uma aba: " + ", ".join(available) + ".")
        sheet = next(iter(available))
    if sheet not in available:
        raise ParseError("Aba não encontrada. Disponíveis: " + ", ".join(available) + ".")
    relation = available[sheet]
    if not _is_relation(relation, "worksheet"):
        raise ParseError("A aba selecionada não é uma planilha de dados.")
    selected = _required(parts, _target(path, relation))
    strings = _shared_strings(_related_part(parts, relations, path, "sharedStrings"))
    style_part = _related_part(parts, relations, path, "styles")
    styles = _styles(style_part)
    return _worksheet(
        selected, sheet, strings, styles, epoch_1904, _conditional_ranges(selected, style_part)
    )


def parse_table(
    content: bytes,
    filename: str,
    *,
    delimiter: str = ";",
    encoding: str = "utf-8-sig",
    sheet: str | None = None,
) -> ParsedTable:
    """Parse CSV/XLSX within fixed limits, or raise a concise Portuguese ParseError.

    CSV encodings/delimiters are explicit; no sniffing or numeric/date inference.
    Sparse XLSX rows are padded with None; mismatched CSV widths and extra XLSX
    data columns quarantine a row. Macros, encryption, unsafe XML and malformed
    package structure reject the file. Links remain inert; formulas never run.
    Excel dates require integral serials (1900 epoch starts at 1, 1904 at 0).
    """
    if len(content) > MAX_UPLOAD_BYTES:
        raise ParseError("Arquivo excede 2 MiB.")
    if not content:
        raise ParseError("Arquivo vazio.")
    if not filename or len(filename) > 255 or "\x00" in filename:
        raise ParseError("Nome de arquivo inválido.")
    if sheet is not None and (not sheet or len(sheet) > 31 or "\x00" in sheet):
        raise ParseError("Nome de aba inválido.")
    extension = posixpath.splitext(filename)[1].lower()
    if extension == ".csv":
        if sheet is not None:
            raise ParseError("CSV não possui abas.")
        return _parse_csv(content, delimiter, encoding)
    if extension == ".xlsx":
        return _parse_xlsx(content, sheet)
    raise ParseError("Envie um arquivo CSV ou XLSX, sem macros.")
