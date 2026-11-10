from datetime import date
from decimal import Decimal as D

import pytest
from hub_finance.ledger import Event, LedgerError, LedgerState, apply_event
from hypothesis import given
from hypothesis import strategies as st

DAY = date(2026, 1, 2)


def funded(amount="10000"):
    state = LedgerState()
    apply_event(state, Event("deposit", DAY, gross_amount=D(amount)))
    return state


def test_deposit_is_not_profit():
    state = funded()
    assert state.cash == state.net_contributions == D("10000")
    assert state.income == state.realized_pnl == 0


def test_independent_purchase_partial_sale_fees_and_split():
    state = funded()
    apply_event(state, Event("buy", DAY, "asset", D("100"), D("20"), fees=D("10")))
    apply_event(state, Event("sell", DAY, "asset", D("40"), D("25"), fees=D("4")))
    # Known independently: total cost 2010, cost of 40 shares 804, proceeds 996.
    assert state.cash == D("8986")
    assert state.positions["asset"].cost_basis == D("1206")
    assert state.realized_pnl == D("192")
    before = state.cash + state.total_cost
    entries = apply_event(state, Event("split", DAY, "asset", D("2")))
    assert state.positions["asset"].quantity == D("120")
    assert state.positions["asset"].cost_basis == D("1206")
    assert state.cash + state.total_cost == before
    assert sum(p.amount for p in entries) == 0


def test_final_sale_consumes_repeating_fraction_cost_exactly():
    state = funded()
    apply_event(state, Event("buy", DAY, "a", D("3"), D("1"), fees=D("0.01")))
    for _ in range(3):
        apply_event(state, Event("sell", DAY, "a", D("1"), D("2")))
    assert state.total_cost == 0
    assert state.positions["a"].quantity == 0
    assert state.realized_pnl == D("2.99")


def test_invalid_event_does_not_mutate_state():
    state = funded("20")
    with pytest.raises(LedgerError, match="Caixa insuficiente"):
        apply_event(state, Event("buy", DAY, "a", D("2"), D("20")))
    assert state.cash == D("20") and not state.positions
    with pytest.raises(LedgerError, match="excede"):
        apply_event(state, Event("sell", DAY, "a", D("1"), D("20")))


def test_income_net_and_separate_expense_reconcile():
    state = funded()
    apply_event(state, Event("dividend", DAY, "a", gross_amount=D("100"), taxes=D("15")))
    apply_event(state, Event("fee", DAY, gross_amount=D("5")))
    assert state.income == D("85")
    assert state.expenses == D("5")
    assert state.cash == D("10080")


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-1", "0.000000001"])
def test_invalid_money_rejected(value):
    with pytest.raises(LedgerError):
        apply_event(LedgerState(), Event("deposit", DAY, gross_amount=D(value)))


@given(st.integers(1, 10000), st.integers(1, 100000))
def test_balanced_journal_and_conservation(quantity, cents):
    q, price = D(quantity), D(cents) / 100
    state = funded("1000000000")
    for event in [
        Event("buy", DAY, "a", q, price),
        Event("split", DAY, "a", D("2")),
        Event("sell", DAY, "a", q * 2, price / 2),
    ]:
        postings = apply_event(state, event)
        assert sum(p.amount for p in postings) == 0
        assert (
            state.cash + state.total_cost
            == state.net_contributions + state.realized_pnl + state.income - state.expenses
        )
    assert state.realized_pnl == 0
