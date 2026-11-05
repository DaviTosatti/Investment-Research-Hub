import hashlib
import json
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, localcontext
from typing import cast

from hub_finance.ledger import (
    METHOD_VERSION,
    ZERO,
    Event,
    EventType,
    LedgerState,
    apply_event,
    decimal_string,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from hub_api.errors import AppError
from hub_api.models import Instrument, Listing, Owner, Portfolio, Price, Transaction, now

MAX_EVENTS = 20000


def domain_event(row: Transaction) -> Event:
    return Event(
        cast(EventType, row.event_type),
        row.trade_date,
        row.instrument_id,
        row.quantity,
        row.unit_price,
        row.gross_amount,
        row.fees,
        row.taxes,
    )


def replay(rows: list[Transaction]) -> LedgerState:
    state = LedgerState()
    for row in rows:
        apply_event(state, domain_event(row))
    return state


def event_rows(db: Session, portfolio_ids: list[str], as_of: date) -> list[Transaction]:
    rows = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.portfolio_id.in_(portfolio_ids), Transaction.trade_date <= as_of)
            .order_by(Transaction.trade_date, Transaction.sequence)
            .limit(MAX_EVENTS + 1)
        )
    )
    if len(rows) > MAX_EVENTS:
        raise AppError(
            422, "RESOURCE_LIMIT", "A consulta excede 20 mil eventos. Selecione uma carteira."
        )
    return rows


def dashboard(db: Session, as_of: date, portfolio_id: str | None, owner_id: str | None) -> dict:
    """Caller uses one repeatable-read transaction for a consistent snapshot."""
    with localcontext() as ctx:
        ctx.prec = 50
        return _dashboard(db, as_of, portfolio_id, owner_id)


def _dashboard(db: Session, as_of: date, portfolio_id: str | None, owner_id: str | None) -> dict:
    query = select(Portfolio)
    if portfolio_id:
        query = query.where(Portfolio.id == portfolio_id)
    if owner_id:
        query = query.where(Portfolio.owner_id == owner_id)
    portfolios = {p.id: p for p in db.scalars(query)}
    if portfolio_id and not portfolios:
        raise AppError(404, "NOT_FOUND", "Carteira não encontrada neste filtro.")
    if owner_id and not db.get(Owner, owner_id):
        raise AppError(404, "NOT_FOUND", "Titular não encontrado.")
    owners = {o.id: o.name for o in db.scalars(select(Owner))}
    rows = event_rows(db, list(portfolios), as_of)
    states = {key: LedgerState() for key in portfolios}
    history = {}
    last_split: dict[tuple[str, str], tuple[date, datetime]] = {}
    for row in rows:
        apply_event(states[row.portfolio_id], domain_event(row))
        if row.event_type == "split":
            last_split[(row.portfolio_id, row.instrument_id)] = (row.trade_date, row.created_at)
        history[row.trade_date] = {
            "date": row.trade_date.isoformat(),
            "net_contributions": decimal_string(
                sum((s.net_contributions for s in states.values()), ZERO)
            ),
            "equity_at_cost": decimal_string(
                sum((s.cash + s.total_cost for s in states.values()), ZERO)
            ),
        }
    instrument_ids = {key for s in states.values() for key, p in s.positions.items() if p.quantity}
    instruments = {
        i.id: (i, listing)
        for i, listing in db.execute(
            select(Instrument, Listing)
            .join(Listing, Listing.instrument_id == Instrument.id)
            .where(Instrument.id.in_(instrument_ids))
        )
    }
    # PostgreSQL DISTINCT ON picks one deterministic newest revision per instrument.
    prices = {
        p.instrument_id: p
        for p in db.scalars(
            select(Price)
            .where(Price.instrument_id.in_(instrument_ids), Price.as_of <= as_of)
            .distinct(Price.instrument_id)
            .order_by(Price.instrument_id, Price.as_of.desc(), Price.sequence.desc())
        )
    }
    positions, warnings = [], []
    allocation: dict[str, Decimal] = defaultdict(lambda: ZERO)
    cash = contributions = income = realized = expenses = cost = market = ZERO
    missing = False
    for key, state in states.items():
        portfolio = portfolios[key]
        cash += state.cash
        contributions += state.net_contributions
        income += state.income
        realized += state.realized_pnl
        expenses += state.expenses
        cost += state.total_cost
        for instrument_id, position in state.positions.items():
            if not position.quantity:
                continue
            instrument, listing = instruments[instrument_id]
            price = prices.get(instrument_id)
            split = last_split.get((key, instrument_id))
            if (
                price
                and split
                and (
                    price.as_of < split[0]
                    or (price.as_of == split[0] and price.retrieved_at <= split[1])
                )
            ):
                price = None
                warnings.append(f"{listing.ticker}: registre uma avaliação após o desdobramento.")
            value = position.quantity * price.price if price else None
            quality = (
                "unavailable"
                if price is None
                else ("stale" if (as_of - price.as_of).days > 7 else "valid")
            )
            if quality != "valid":
                warnings.append(
                    f"{listing.ticker}: avaliação {'ausente' if price is None else 'desatualizada'}."
                )
            if value is None:
                missing = True
            else:
                market += value
            allocation[instrument.asset_class] += position.cost_basis
            positions.append(
                {
                    "portfolio_id": key,
                    "portfolio_name": portfolio.name,
                    "owner_name": owners[portfolio.owner_id],
                    "instrument_id": instrument_id,
                    "ticker": listing.ticker,
                    "name": instrument.name,
                    "asset_class": instrument.asset_class,
                    "quantity": decimal_string(position.quantity),
                    "cost_basis": decimal_string(position.cost_basis),
                    "average_cost": decimal_string(position.cost_basis / position.quantity),
                    "last_price": decimal_string(price.price) if price else None,
                    "price_as_of": price.as_of.isoformat() if price else None,
                    "price_source": price.source if price else None,
                    "market_value": decimal_string(value) if value is not None else None,
                    "unrealized_pnl": decimal_string(value - position.cost_basis)
                    if value is not None
                    else None,
                    "quality": quality,
                }
            )
    activity = [
        {
            "id": r.id,
            "event_type": r.event_type,
            "ticker": db.scalar(
                select(Listing.ticker).where(Listing.instrument_id == r.instrument_id)
            )
            if r.instrument_id
            else None,
            "portfolio_name": portfolios[r.portfolio_id].name,
            "owner_name": owners[r.owner_id],
            "gross_amount": decimal_string(r.gross_amount),
            "trade_date": r.trade_date.isoformat(),
        }
        for r in reversed(rows[-8:])
    ]
    fingerprint = json.dumps(
        {
            "events": [r.id for r in rows],
            "prices": sorted(p.id for p in prices.values()),
            "as_of": as_of.isoformat(),
            "portfolios": sorted(portfolios),
            "method": METHOD_VERSION,
        },
        sort_keys=True,
    ).encode()
    warnings += [
        "Avaliações manuais; histórico de patrimônio a custo. Rentabilidade TWR/MWR ainda indisponível.",
        "Caixa reconhecido por data de negociação; não representa saldo liquidado para saque.",
    ]
    return {
        "as_of": as_of.isoformat(),
        "currency": "BRL",
        "generated_at": now().isoformat(),
        "snapshot_id": hashlib.sha256(fingerprint).hexdigest(),
        "method_version": METHOD_VERSION,
        "summary": {
            "cash": decimal_string(cash),
            "net_contributions": decimal_string(contributions),
            "income": decimal_string(income),
            "realized_pnl": decimal_string(realized),
            "expenses": decimal_string(expenses),
            "total_cost": decimal_string(cost),
            "equity_at_cost": decimal_string(cash + cost),
            "market_value": None if missing else decimal_string(market),
            "equity": None if missing else decimal_string(cash + market),
            "unrealized_pnl": None if missing else decimal_string(market - cost),
            "performance": None,
            "performance_reason": "Séries de avaliações e fluxos para TWR/MWR ainda pendentes.",
        },
        "positions": sorted(positions, key=lambda p: (p["ticker"], p["portfolio_name"])),
        "history": list(history.values()),
        "allocation": [
            {
                "asset_class": key,
                "cost_basis": decimal_string(value),
                "weight": decimal_string(value / cost * 100 if cost else ZERO),
            }
            for key, value in sorted(allocation.items())
        ],
        "activity": activity,
        "warnings": list(dict.fromkeys(warnings)),
    }
