import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def identifier() -> str:
    return str(uuid.uuid4())


def now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    __table_args__ = (CheckConstraint("role IN ('admin','member','viewer')"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(16))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    failures: Mapped[int] = mapped_column(Integer, default=0)
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Owner(Base):
    __tablename__ = "owners"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(100))


class Account(Base):
    __tablename__ = "broker_accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    owner_id: Mapped[str] = mapped_column(ForeignKey("owners.id"))
    name: Mapped[str] = mapped_column(String(120))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")


class Portfolio(Base):
    __tablename__ = "portfolios"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    owner_id: Mapped[str] = mapped_column(ForeignKey("owners.id"), index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("broker_accounts.id"))
    name: Mapped[str] = mapped_column(String(100))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class Issuer(Base):
    __tablename__ = "issuers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(160))


class Instrument(Base):
    __tablename__ = "instruments"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    issuer_id: Mapped[str | None] = mapped_column(ForeignKey("issuers.id"))
    name: Mapped[str] = mapped_column(String(160))
    asset_class: Mapped[str] = mapped_column(String(24))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (UniqueConstraint("exchange", "ticker"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id"), unique=True)
    exchange: Mapped[str] = mapped_column(String(24))
    ticker: Mapped[str] = mapped_column(String(24))
    valid_from: Mapped[date | None] = mapped_column(Date)
    valid_to: Mapped[date | None] = mapped_column(Date)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "idempotency_key"),
        UniqueConstraint("portfolio_id", "source", "external_id"),
        Index("ix_transactions_timeline", "portfolio_id", "trade_date", "sequence"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)
    portfolio_id: Mapped[str] = mapped_column(ForeignKey("portfolios.id"))
    owner_id: Mapped[str] = mapped_column(ForeignKey("owners.id"))
    broker_account_id: Mapped[str] = mapped_column(ForeignKey("broker_accounts.id"))
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.id"))
    event_type: Mapped[str] = mapped_column(String(24))
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    gross_amount: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    fees: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    taxes: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    trade_date: Mapped[date] = mapped_column(Date)
    settlement_date: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(120))
    external_id: Mapped[str | None] = mapped_column(String(160))
    idempotency_key: Mapped[str] = mapped_column(String(128))
    payload_hash: Mapped[str] = mapped_column(String(64))
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    revision: Mapped[int] = mapped_column(Integer, default=1)


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), index=True)
    account: Mapped[str] = mapped_column(String(32))
    amount: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    instrument_id: Mapped[str | None] = mapped_column(ForeignKey("instruments.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(38, 16))


class Price(Base):
    __tablename__ = "prices"
    __table_args__ = (Index("ix_prices_snapshot", "instrument_id", "as_of", "sequence"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    sequence: Mapped[int] = mapped_column(BigInteger, Identity(), unique=True)
    instrument_id: Mapped[str] = mapped_column(ForeignKey("instruments.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(38, 16))
    as_of: Mapped[date] = mapped_column(Date)
    source: Mapped[str] = mapped_column(String(200))
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    raw_payload_hash: Mapped[str] = mapped_column(String(64))


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    actor_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(80))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    name: Mapped[str] = mapped_column(String(120))
    name_key: Mapped[str] = mapped_column(String(120), unique=True)
    kind: Mapped[str] = mapped_column(String(24), default="statement_upload")
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class OriginalFile(Base):
    __tablename__ = "original_files"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    sha256: Mapped[str] = mapped_column(String(64), unique=True)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    size: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ImportBatch(Base):
    __tablename__ = "import_batches"
    __table_args__ = (
        UniqueConstraint("portfolio_id", "source_id", "original_id", "parse_key"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    portfolio_id: Mapped[str] = mapped_column(ForeignKey("portfolios.id"), index=True)
    source_id: Mapped[str] = mapped_column(ForeignKey("data_sources.id"))
    original_id: Mapped[str] = mapped_column(ForeignKey("original_files.id"))
    filename: Mapped[str] = mapped_column(String(180))
    parse_key: Mapped[str] = mapped_column(String(64))
    parse_options: Mapped[dict] = mapped_column(JSON)
    table: Mapped[dict] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ImportPreview(Base):
    __tablename__ = "import_previews"
    __table_args__ = (UniqueConstraint("import_id", "revision"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    import_id: Mapped[str] = mapped_column(ForeignKey("import_batches.id"), index=True)
    revision: Mapped[int] = mapped_column(Integer)
    ledger_version: Mapped[str] = mapped_column(String(64))
    config: Mapped[dict] = mapped_column(JSON)
    rows: Mapped[list] = mapped_column(JSON)
    summary: Mapped[dict] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)


class ImportReceipt(Base):
    __tablename__ = "import_receipts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=identifier)
    import_id: Mapped[str] = mapped_column(ForeignKey("import_batches.id"), unique=True)
    preview_id: Mapped[str] = mapped_column(ForeignKey("import_previews.id"), unique=True)
    results: Mapped[list] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
