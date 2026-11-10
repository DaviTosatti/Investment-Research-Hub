"""Independent accounting regressions from numerical review.

Dashboard tests supply already-selected ORM rows, so they validate accounting,
not PostgreSQL query execution or HTTP authorization.
"""

from copy import deepcopy
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal as D
from decimal import localcontext
from unittest.mock import Mock

import pytest
from hub_api import portfolio_service
from hub_api.models import Instrument, Listing, Owner, Portfolio, Price, Transaction
from hub_finance.ledger import Event, LedgerError, LedgerState, apply_event
from sqlalchemy.orm import Session

DAY = date(2026, 1, 2)
NEXT_DAY = date(2026, 1, 3)


def funded(amount="100"):
    state = LedgerState()
    apply_event(state, Event("deposit", DAY, gross_amount=D(amount)))
    return state


def assert_conserved(state):
    with localcontext() as context:
        context.prec = 80
        assert state.cash + state.total_cost == (
            state.net_contributions + state.realized_pnl + state.income - state.expenses
        )


def test_reverse_split_round_trip_preserves_economic_ownership_and_cost():
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("12.5"), D("2"), fees=D("0.01")))
    before = deepcopy(state)
    apply_event(state, Event("split", DAY, "asset", D("0.2")))
    assert state.positions["asset"].quantity == D("2.5")
    assert state.positions["asset"].cost_basis == D("25.01")
    apply_event(state, Event("split", DAY, "asset", D("5")))
    assert state == before
    assert_conserved(state)


def test_zero_remaining_cost_does_not_erase_remaining_ownership():
    state = funded("0.01")
    apply_event(state, Event("buy", DAY, "asset", D("1"), D("0.01")))
    apply_event(state, Event("split", DAY, "asset", D("100000000")))
    apply_event(state, Event("sell", DAY, "asset", D("99999999.99999999"), D("0.00000001")))
    assert state.positions["asset"].quantity == D("0.00000001")
    assert state.positions["asset"].cost_basis == 0
    assert state.realized_pnl == D("0.99")
    assert_conserved(state)
    apply_event(state, Event("sell", DAY, "asset", D("0.00000001"), D("1000000")))
    assert state.positions["asset"].quantity == state.total_cost == 0
    assert state.cash == D("1.01")
    assert state.realized_pnl == D("1.00")
    assert_conserved(state)


def test_sale_charges_exceeding_proceeds_are_funded_and_counted_once():
    state = funded("10")
    apply_event(state, Event("buy", DAY, "asset", D("1"), D("1")))
    postings = apply_event(
        state, Event("sell", DAY, "asset", D("1"), D("0.01"), fees=D("0.02"), taxes=D("0.01"))
    )
    assert state.cash == D("8.98")
    assert state.realized_pnl == D("-1.02")
    assert state.expenses == 0
    assert sum(p.amount for p in postings) == 0
    assert_conserved(state)


@pytest.mark.parametrize("field", ["quantity", "unit_price", "gross_amount", "fees", "taxes"])
@pytest.mark.parametrize("value", ["sNaN", "-Infinity"])
def test_nonfinite_fields_are_domain_errors_and_leave_whole_state_unchanged(field, value):
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("3"), D("1"), fees=D("0.01")))
    before = deepcopy(state)
    event = replace(Event("sell", DAY, "asset", D("1"), D("2")), **{field: D(value)})
    with pytest.raises(LedgerError):
        apply_event(state, event)
    assert state == before


@pytest.mark.parametrize(
    "event",
    [
        Event("dividend", DAY, "asset", gross_amount=D("1.001")),
        Event("dividend", DAY, "asset", gross_amount=D("1"), taxes=D("1.01")),
        Event("sell", DAY, "asset", D("1"), D("2"), gross_amount=D("1.99")),
        Event("sell", DAY, "asset", D("1"), D("2"), fees=D("0.001")),
        Event("split", DAY, "asset", D("2"), gross_amount=D("1")),
        Event("split", DAY, "asset", D("2"), taxes=D("0.01")),
        Event("deposit", DAY, "asset", gross_amount=D("1")),
    ],
)
def test_invalid_fields_do_not_partially_mutate_existing_positions(event):
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("3"), D("1"), fees=D("0.01")))
    before = deepcopy(state)
    with pytest.raises(LedgerError):
        apply_event(state, event)
    assert state == before


def test_reverse_split_rejects_unrepresentable_fraction_atomically():
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("0.00000001"), D("1000000")))
    before = deepcopy(state)
    with pytest.raises(LedgerError, match="frações"):
        apply_event(state, Event("split", DAY, "asset", D("0.1")))
    assert state == before


def test_split_rejects_numeric_38_16_quantity_overflow_atomically():
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("1"), D("1")))
    for _ in range(2):
        apply_event(state, Event("split", DAY, "asset", D("1000000000")))
    before = deepcopy(state)
    with pytest.raises(LedgerError, match="armazenamento"):
        apply_event(state, Event("split", DAY, "asset", D("1000000000")))
    assert state == before


def test_total_cost_preserves_all_16_decimal_places_of_reachable_position():
    state = LedgerState()
    for index in range(151):
        apply_event(state, Event("deposit", DAY, gross_amount=D("9999999999.99")))
        apply_event(
            state,
            Event(
                "buy",
                DAY,
                "asset",
                D("1"),
                D("9999999999"),
                fees=D("0.01") if index == 0 else D("0"),
            ),
        )
    apply_event(state, Event("sell", DAY, "asset", D("1"), D("1")))
    with localcontext() as context:
        context.prec = 28
        assert state.total_cost == state.positions["asset"].cost_basis


def test_accepted_trade_can_be_replayed_with_its_materialized_gross():
    state = LedgerState()
    for _ in range(2):
        apply_event(state, Event("deposit", DAY, gross_amount=D("6000000000")))
    replayed = deepcopy(state)
    event = Event("buy", DAY, "asset", D("2"), D("6000000000"))
    apply_event(state, event)
    apply_event(replayed, replace(event, gross_amount=D("12000000000")))
    assert state == replayed


def transaction(sequence, event, portfolio="p1", owner="o1"):
    return Transaction(
        id=f"t{sequence}",
        sequence=sequence,
        portfolio_id=portfolio,
        owner_id=owner,
        instrument_id=event.instrument_id,
        event_type=event.event_type,
        quantity=event.quantity,
        unit_price=event.unit_price,
        gross_amount=event.gross_amount,
        fees=event.fees,
        taxes=event.taxes,
        trade_date=event.trade_date,
        created_at=datetime(2026, 1, 3, 15, tzinfo=UTC),
    )


def selected_dashboard(monkeypatch, rows, prices=(), portfolios=None, owners=None):
    db = Mock(spec=Session)
    db.scalars.side_effect = [
        portfolios or [Portfolio(id="p1", name="One", owner_id="o1")],
        owners or [Owner(id="o1", name="Owner one")],
        prices,
    ]
    db.execute.return_value = [
        (
            Instrument(id="asset", name="Asset", asset_class="stock"),
            Listing(instrument_id="asset", ticker="TEST3"),
        ),
    ]
    db.scalar.return_value = "TEST3"
    monkeypatch.setattr(portfolio_service, "event_rows", lambda *args: rows)
    return portfolio_service.dashboard(db, NEXT_DAY, None, None)


@pytest.mark.parametrize(
    "factor,quote_day",
    [
        ("2", DAY),
        ("0.5", DAY),
        ("2", NEXT_DAY),
        ("0.5", NEXT_DAY),
    ],
)
def test_pre_action_quote_cannot_create_phantom_gain_or_loss(monkeypatch, factor, quote_day):
    rows = [
        transaction(1, Event("deposit", DAY, gross_amount=D("1000"))),
        transaction(2, Event("buy", DAY, "asset", D("100"), D("10"))),
        transaction(3, Event("split", NEXT_DAY, "asset", D(factor))),
    ]
    quote = Price(
        id="quote",
        instrument_id="asset",
        price=D("10"),
        as_of=quote_day,
        source="manual before action",
        retrieved_at=datetime(2026, 1, 3, 10, tzinfo=UTC),
    )
    report = selected_dashboard(monkeypatch, rows, [quote])
    assert D(report["summary"]["equity_at_cost"]) == D("1000")
    assert report["summary"]["equity"] is None
    assert report["summary"]["unrealized_pnl"] is None
    assert report["positions"][0]["quality"] == "unavailable"


@pytest.mark.parametrize("factor,adjusted_price", [("2", "5"), ("0.5", "20")])
def test_fresh_same_day_post_action_quote_preserves_equity(monkeypatch, factor, adjusted_price):
    rows = [
        transaction(1, Event("deposit", DAY, gross_amount=D("1000"))),
        transaction(2, Event("buy", DAY, "asset", D("100"), D("10"))),
        transaction(3, Event("split", NEXT_DAY, "asset", D(factor))),
    ]
    quote = Price(
        id="quote",
        instrument_id="asset",
        price=D(adjusted_price),
        as_of=NEXT_DAY,
        source="manual after action",
        retrieved_at=datetime(2026, 1, 3, 16, tzinfo=UTC),
    )
    report = selected_dashboard(monkeypatch, rows, [quote])
    assert D(report["summary"]["equity"]) == D("1000")
    assert D(report["summary"]["unrealized_pnl"]) == 0
    assert report["positions"][0]["quality"] == "valid"


def test_owner_results_and_costs_are_separate_with_offsetting_results(monkeypatch):
    rows = [
        transaction(1, Event("deposit", DAY, gross_amount=D("100"))),
        transaction(2, Event("buy", DAY, "asset", D("2"), D("10"))),
        transaction(3, Event("deposit", DAY, gross_amount=D("100")), "p2", "o2"),
        transaction(4, Event("buy", DAY, "asset", D("2"), D("30")), "p2", "o2"),
        transaction(5, Event("sell", NEXT_DAY, "asset", D("1"), D("20"))),
        transaction(6, Event("sell", NEXT_DAY, "asset", D("1"), D("20")), "p2", "o2"),
    ]
    first = portfolio_service.replay([row for row in rows if row.portfolio_id == "p1"])
    second = portfolio_service.replay([row for row in rows if row.portfolio_id == "p2"])
    assert first.realized_pnl == D("10")
    assert second.realized_pnl == D("-10")
    report = selected_dashboard(
        monkeypatch,
        rows,
        portfolios=[
            Portfolio(id="p1", name="One", owner_id="o1"),
            Portfolio(id="p2", name="Two", owner_id="o2"),
        ],
        owners=[Owner(id="o1", name="Owner one"), Owner(id="o2", name="Owner two")],
    )
    positions = {p["owner_name"]: p for p in report["positions"]}
    assert D(positions["Owner one"]["cost_basis"]) == D("10")
    assert D(positions["Owner two"]["cost_basis"]) == D("30")
    assert D(report["summary"]["equity_at_cost"]) == D("200")
    assert report["summary"]["equity"] is None


def test_same_day_sale_then_repurchase_retains_sequence_specific_average_cost():
    events = [
        Event("deposit", DAY, gross_amount=D("100")),
        Event("buy", DAY, "asset", D("2"), D("10")),
        Event("sell", DAY, "asset", D("1"), D("15")),
        Event("buy", DAY, "asset", D("1"), D("40")),
    ]
    state = portfolio_service.replay([transaction(i, e) for i, e in enumerate(events)])
    assert state.positions["asset"].quantity == D("2")
    assert state.positions["asset"].cost_basis == D("50")
    assert state.realized_pnl == D("5")
    assert state.cash == D("55")
    assert_conserved(state)
