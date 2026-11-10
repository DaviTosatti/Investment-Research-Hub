from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

Role = Literal["admin", "member", "viewer"]
AssetClass = Literal["stock", "fii", "etf", "fixed_income", "other"]


def exact_decimal_input(value):
    if not isinstance(value, (str, Decimal)):
        raise ValueError("Envie valores decimais como texto para preservar precisão.")
    return value


Amount = Annotated[
    Decimal,
    BeforeValidator(exact_decimal_input),
    Field(ge=0, lt=Decimal("10000000000"), max_digits=18, decimal_places=8),
]
Name = Annotated[str, Field(min_length=1, max_length=100)]


def today() -> date:
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


class Input(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Input):
    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=128)]

    @field_validator("email")
    @classmethod
    def email_lower(cls, value: str) -> str:
        return value.lower()


class MemberCreate(Login):
    name: Name
    password: Annotated[str, Field(min_length=12, max_length=128)]
    role: Role = "member"


class OwnerCreate(Input):
    name: Name


class PortfolioCreate(Input):
    name: Name
    owner_id: UUID
    account_name: Annotated[str, Field(min_length=1, max_length=120)]
    currency: Literal["BRL"] = "BRL"


class InstrumentCreate(Input):
    ticker: Annotated[str, Field(min_length=1, max_length=24, pattern=r"^[A-Za-z0-9._-]+$")]
    name: Annotated[str, Field(min_length=1, max_length=160)]
    asset_class: AssetClass
    currency: Literal["BRL"] = "BRL"
    exchange: Annotated[str, Field(min_length=1, max_length=24)] = "B3"
    issuer_name: Annotated[str | None, Field(min_length=1, max_length=160)] = None


class PriceCreate(Input):
    instrument_id: UUID
    price: Amount
    as_of: date
    source: Annotated[str, Field(min_length=1, max_length=200)]

    @model_validator(mode="after")
    def valid_price(self):
        if self.price <= 0 or self.as_of > today():
            raise ValueError("Preço deve ser positivo e a data não pode ser futura.")
        return self


class TransactionCreate(Input):
    portfolio_id: UUID
    instrument_id: UUID | None = None
    event_type: Literal["deposit", "withdrawal", "buy", "sell", "dividend", "fee", "tax", "split"]
    quantity: Amount = Decimal("0")
    unit_price: Amount = Decimal("0")
    gross_amount: Amount = Decimal("0")
    fees: Amount = Decimal("0")
    taxes: Amount = Decimal("0")
    trade_date: date
    settlement_date: date | None = None
    source: Annotated[str, Field(min_length=1, max_length=120)] = "manual"
    external_id: Annotated[str | None, Field(min_length=1, max_length=160)] = None
    idempotency_key: Annotated[str, Field(min_length=8, max_length=128)]
    notes: Annotated[str | None, Field(max_length=2000)] = None

    @model_validator(mode="after")
    def valid_dates(self):
        if self.trade_date > today():
            raise ValueError("Registre apenas operações já realizadas.")
        if self.settlement_date is None:
            self.settlement_date = self.trade_date
        if self.settlement_date < self.trade_date:
            raise ValueError("Liquidação não pode anteceder a negociação.")
        return self
