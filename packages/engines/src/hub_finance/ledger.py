"""Versioned, trade-date, average-cost ledger. All amounts are exact Decimal."""

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_EVEN, Decimal, localcontext
from typing import Literal

METHOD_VERSION = "average-cost-brl/1.0.1"
ZERO = Decimal("0")
MONEY = Decimal("0.01")
INTERNAL = Decimal("0.0000000000000001")
EventType = Literal["deposit", "withdrawal", "buy", "sell", "dividend", "fee", "tax", "split"]


class LedgerError(ValueError):
    """An event would violate accounting or the supported instrument rules."""


@dataclass(frozen=True)
class Event:
    event_type: EventType
    trade_date: date
    instrument_id: str | None = None
    quantity: Decimal = ZERO
    unit_price: Decimal = ZERO
    gross_amount: Decimal = ZERO
    fees: Decimal = ZERO
    taxes: Decimal = ZERO


@dataclass(frozen=True)
class Posting:
    account: str
    amount: Decimal
    instrument_id: str | None = None
    quantity: Decimal = ZERO


@dataclass
class Position:
    quantity: Decimal = ZERO
    cost_basis: Decimal = ZERO


@dataclass
class LedgerState:
    cash: Decimal = ZERO
    net_contributions: Decimal = ZERO
    income: Decimal = ZERO
    realized_pnl: Decimal = ZERO
    expenses: Decimal = ZERO
    positions: dict[str, Position] = field(default_factory=dict)

    @property
    def total_cost(self) -> Decimal:
        with localcontext() as ctx:
            ctx.prec = 50
            return sum((p.cost_basis for p in self.positions.values()), ZERO)


def cash_amount(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_EVEN)


def decimal_string(value: Decimal) -> str:
    return format(value, "f")


def event_gross(event: Event) -> Decimal:
    """Canonical gross, also used by persistence; no float or ambient rounding."""
    with localcontext() as ctx:
        ctx.prec = 50
        return (
            cash_amount(event.quantity * event.unit_price)
            if event.event_type in {"buy", "sell"}
            else event.gross_amount
        )


def apply_event(state: LedgerState, event: Event) -> list[Posting]:
    """Apply one valid event atomically in memory; return a balanced journal.

    Inputs and quantities keep up to eight decimals; gross cash is rounded once
    to BRL cents (half-even). Partial-sale allocated cost keeps 16 decimals;
    a final sale consumes the exact remaining cost, preventing residual dust.
    """
    with localcontext() as ctx:
        ctx.prec = 50
        return _apply(state, event)


def _apply(state: LedgerState, event: Event) -> list[Posting]:
    kind = event.event_type
    if kind not in {"deposit", "withdrawal", "buy", "sell", "dividend", "fee", "tax", "split"}:
        raise LedgerError("Tipo de evento não suportado.")
    for value in (event.quantity, event.unit_price, event.fees, event.taxes):
        if not value.is_finite() or value < ZERO or value >= Decimal("10000000000"):
            raise LedgerError("Valores devem ser finitos, não negativos e inferiores a 10 bilhões.")
        if value != value.quantize(Decimal("0.00000001")):
            raise LedgerError("Valores de entrada admitem até oito casas decimais.")
    if event.fees != cash_amount(event.fees) or event.taxes != cash_amount(event.taxes):
        raise LedgerError("Taxas e impostos em reais admitem até duas casas decimais.")
    trading = kind in {"buy", "sell"}
    gross_limit = Decimal("100000000000000000000") if trading else Decimal("10000000000")
    if (
        not event.gross_amount.is_finite()
        or event.gross_amount < ZERO
        or event.gross_amount >= gross_limit
    ):
        raise LedgerError("Valor bruto inválido ou acima do limite de armazenamento.")
    if (trading or kind == "split") and (not event.instrument_id or event.quantity <= ZERO):
        raise LedgerError("Informe o ativo e uma quantidade ou fator positivo.")
    if trading and event.unit_price <= ZERO:
        raise LedgerError("Preço unitário deve ser positivo.")
    if not trading and kind != "split" and event.gross_amount <= ZERO:
        raise LedgerError("Informe um valor bruto positivo.")
    if not trading and kind != "dividend" and (event.fees or event.taxes):
        raise LedgerError("Registre taxas e impostos separadamente para este evento.")
    if not trading and (event.unit_price or (event.quantity and kind != "split")):
        raise LedgerError("Quantidade/preço não se aplicam a este evento.")
    if kind == "split" and event.gross_amount:
        raise LedgerError("Desdobramento não movimenta dinheiro.")
    if kind in {"deposit", "withdrawal", "fee", "tax"} and event.instrument_id:
        raise LedgerError("Este evento pertence ao caixa, sem ativo associado.")

    gross = event_gross(event)
    if kind != "split" and (gross <= ZERO or gross != cash_amount(gross)):
        raise LedgerError("O valor bruto de caixa deve ser positivo e expresso em centavos.")
    if trading and event.gross_amount not in (ZERO, gross):
        raise LedgerError("Valor bruto diverge de quantidade vezes preço.")
    charges = event.fees + event.taxes
    instrument = event.instrument_id
    position = state.positions.get(instrument or "", Position())
    entries: list[Posting]
    cash_delta = ZERO
    contributed = income = realized = expenses = ZERO
    next_quantity, next_cost = position.quantity, position.cost_basis
    if kind == "deposit":
        cash_delta, contributed = gross, gross
        entries = [Posting("cash", gross), Posting("contributed_capital", -gross)]
    elif kind == "withdrawal":
        cash_delta, contributed = -gross, -gross
        entries = [Posting("cash", -gross), Posting("contributed_capital", gross)]
    elif kind == "buy":
        cash_delta = -(gross + charges)
        next_quantity += event.quantity
        next_cost += gross + charges
        entries = [
            Posting("cash", cash_delta),
            Posting("asset_cost", -cash_delta, instrument, event.quantity),
        ]
    elif kind == "sell":
        if event.quantity > position.quantity:
            raise LedgerError(
                "Venda excede a posição disponível; venda a descoberto não suportada."
            )
        removed = (
            position.cost_basis
            if event.quantity == position.quantity
            else (position.cost_basis * event.quantity / position.quantity).quantize(
                INTERNAL, rounding=ROUND_HALF_EVEN
            )
        )
        cash_delta = gross - charges
        next_quantity -= event.quantity
        next_cost -= removed
        realized = cash_delta - removed
        entries = [
            Posting("cash", cash_delta),
            Posting("asset_cost", -removed, instrument, -event.quantity),
            Posting("realized_result", -realized),
        ]
    elif kind == "dividend":
        cash_delta = gross - charges
        income = cash_delta
        if cash_delta < ZERO:
            raise LedgerError("Descontos excedem o provento bruto.")
        entries = [
            Posting("cash", cash_delta),
            Posting("income", -gross),
            Posting("income_deductions", charges),
        ]
    elif kind in {"fee", "tax"}:
        cash_delta, expenses = -gross, gross
        entries = [Posting("cash", -gross), Posting("expenses", gross)]
    else:
        if position.quantity <= ZERO:
            raise LedgerError("Desdobramento exige uma posição existente.")
        next_quantity = position.quantity * event.quantity
        if next_quantity != next_quantity.quantize(Decimal("0.00000001")):
            raise LedgerError(
                "Fator gera frações sem tratamento; registre a conciliação do evento."
            )
        entries = [Posting("asset_cost", ZERO, instrument, next_quantity - position.quantity)]

    if state.cash + cash_delta < ZERO:
        raise LedgerError("Caixa insuficiente na data do evento; confira os aportes anteriores.")
    if next_quantity >= Decimal("10000000000000000000000"):
        raise LedgerError("Quantidade resultante excede o limite de armazenamento.")
    if next_cost >= Decimal("10000000000000000000000"):
        raise LedgerError("Custo resultante excede o limite de armazenamento.")
    if sum((p.amount for p in entries), ZERO) != ZERO:
        raise LedgerError("Lançamento não balanceado.")
    state.cash += cash_delta
    state.net_contributions += contributed
    state.income += income
    state.realized_pnl += realized
    state.expenses += expenses
    if instrument and kind in {"buy", "sell", "split"}:
        state.positions[instrument] = Position(next_quantity, next_cost)
    return entries
