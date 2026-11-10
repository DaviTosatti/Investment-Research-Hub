"""Validated public responses; financial Decimal fields serialize as JSON strings."""

from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from hub_api.schemas import AssetClass, Role


class Page[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int


class UserRead(BaseModel):
    id: UUID
    name: str
    email: str
    role: Role


class AuthRead(BaseModel):
    user: UserRead


class OwnerRead(BaseModel):
    id: UUID
    name: str


class PortfolioRead(BaseModel):
    id: UUID
    name: str
    owner_id: UUID
    owner_name: str
    account_name: str
    currency: Literal["BRL"]
    created_at: datetime


class InstrumentRead(BaseModel):
    id: UUID
    name: str
    asset_class: AssetClass
    currency: Literal["BRL"]
    ticker: str
    exchange: str


class PriceRead(BaseModel):
    id: UUID
    instrument_id: UUID
    price: Decimal
    as_of: date
    source: str
    retrieved_at: datetime


class TransactionRead(BaseModel):
    id: UUID
    portfolio_id: UUID
    portfolio_name: str
    owner_name: str
    instrument_id: UUID | None
    ticker: str | None
    event_type: str
    quantity: Decimal
    unit_price: Decimal
    gross_amount: Decimal
    fees: Decimal
    taxes: Decimal
    trade_date: date
    settlement_date: date
    source: str
    external_id: str | None
    notes: str | None
    created_by: UUID
    created_at: datetime
    revision: int


class SummaryRead(BaseModel):
    cash: Decimal
    net_contributions: Decimal
    income: Decimal
    realized_pnl: Decimal
    expenses: Decimal
    total_cost: Decimal
    equity_at_cost: Decimal
    market_value: Decimal | None
    equity: Decimal | None
    unrealized_pnl: Decimal | None
    performance: None
    performance_reason: str


class PositionRead(BaseModel):
    portfolio_id: UUID
    portfolio_name: str
    owner_name: str
    instrument_id: UUID
    ticker: str
    name: str
    asset_class: AssetClass
    quantity: Decimal
    cost_basis: Decimal
    average_cost: Decimal
    last_price: Decimal | None
    price_as_of: date | None
    price_source: str | None
    market_value: Decimal | None
    unrealized_pnl: Decimal | None
    quality: Literal["valid", "stale", "unavailable"]


class HistoryRead(BaseModel):
    date: date
    net_contributions: Decimal
    equity_at_cost: Decimal


class AllocationRead(BaseModel):
    asset_class: AssetClass
    cost_basis: Decimal
    weight: Decimal


class ActivityRead(BaseModel):
    id: UUID
    event_type: str
    ticker: str | None
    portfolio_name: str
    owner_name: str
    gross_amount: Decimal
    trade_date: date


class DashboardRead(BaseModel):
    as_of: date
    currency: Literal["BRL"]
    generated_at: datetime
    snapshot_id: str
    method_version: str
    summary: SummaryRead
    positions: list[PositionRead]
    history: list[HistoryRead]
    allocation: list[AllocationRead]
    activity: list[ActivityRead]
    warnings: list[str]


class AuditRead(BaseModel):
    id: str
    action: str
    entity_type: str
    entity_id: UUID
    actor_name: str
    created_at: datetime
