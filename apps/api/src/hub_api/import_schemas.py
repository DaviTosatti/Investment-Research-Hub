from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, model_validator

from hub_api.schemas import Input

ImportField = Literal[
    "event_type",
    "trade_date",
    "settlement_date",
    "ticker",
    "exchange",
    "instrument_id",
    "quantity",
    "unit_price",
    "gross_amount",
    "fees",
    "taxes",
    "external_id",
    "notes",
    "currency",
]


class ImportInput(Input):
    @model_validator(mode="before")
    @classmethod
    def safe_text(cls, value):
        pending = [value]
        while pending:
            item = pending.pop()
            if isinstance(item, dict):
                pending.extend(item.keys())
                pending.extend(item.values())
            elif isinstance(item, list):
                pending.extend(item)
            elif isinstance(item, str):
                if "\x00" in item:
                    raise ValueError("Texto contém NUL, não permitido.")
                try:
                    item.encode("utf-8", errors="strict")
                except UnicodeEncodeError as exc:
                    raise ValueError("Texto contém caracteres Unicode inválidos.") from exc
        return value


class SourceCreate(ImportInput):
    name: Annotated[str, Field(min_length=1, max_length=120)]


class RowEdit(ImportInput):
    row_number: Annotated[int, Field(ge=2)]
    values: dict[ImportField, Annotated[str | None, Field(max_length=2000)]]
    reason: Annotated[str, Field(min_length=5, max_length=500)]


class RowDecision(ImportInput):
    row_number: Annotated[int, Field(ge=2)]
    action: Literal["skip", "create"]
    reason: Annotated[str, Field(min_length=5, max_length=500)]


class PreviewCreate(ImportInput):
    mapping: dict[ImportField, Annotated[str, Field(min_length=1, max_length=200)]]
    decimal_separator: Literal[".", ","] = "."
    date_format: Literal["YYYY-MM-DD", "DD/MM/YYYY"] = "YYYY-MM-DD"
    exchange: Annotated[str, Field(min_length=1, max_length=24)] = "B3"
    event_values: Annotated[
        dict[
            str,
            Literal[
                "deposit",
                "withdrawal",
                "buy",
                "sell",
                "dividend",
                "fee",
                "tax",
                "split",
            ],
        ],
        Field(max_length=40),
    ] = Field(default_factory=dict)
    edits: Annotated[list[RowEdit], Field(max_length=500)] = Field(default_factory=list)
    decisions: Annotated[list[RowDecision], Field(max_length=500)] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_mapping(self):
        if not {"event_type", "trade_date"}.issubset(self.mapping):
            raise ValueError("Mapeie o tipo de evento e a data da operação.")
        if len(set(self.mapping.values())) != len(self.mapping):
            raise ValueError("Cada coluna deve corresponder a um único campo.")
        for values in (self.edits, self.decisions):
            if len({v.row_number for v in values}) != len(values):
                raise ValueError("Informe uma única alteração ou decisão por linha.")
        return self


class ImportConfirm(ImportInput):
    preview_id: UUID
