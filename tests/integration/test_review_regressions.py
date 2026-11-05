"""Bounded review regressions against the isolated PostgreSQL fixture."""

import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal as D
from threading import Barrier

from fastapi.testclient import TestClient
from hub_api import portfolio_service
from hub_api.models import AuthSession, JournalEntry, LoginAttempt, Transaction, User
from hub_api.schemas import today
from hub_api.security import digest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

PASSWORD = "test-only-password-123"


def record(client, portfolio, kind, **values):
    return client.post(
        "/api/v1/transactions",
        json={
            "portfolio_id": portfolio["id"],
            "event_type": kind,
            "trade_date": str(today()),
            "idempotency_key": str(uuid.uuid4()),
            **values,
        },
    )


def test_distinct_concurrent_withdrawals_cannot_spend_the_same_cash(client, app, portfolio):
    assert record(client, portfolio, "deposit", gross_amount="100").status_code == 201
    token = client.cookies.get("hub_session")
    barrier = Barrier(2)

    def withdraw():
        with TestClient(
            app, headers={"X-Hub-Request": "1", "Cookie": f"hub_session={token}"}
        ) as other:
            barrier.wait(timeout=5)
            return record(other, portfolio, "withdrawal", gross_amount="80").status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        requests = [pool.submit(withdraw) for _ in range(2)]
        assert sorted(request.result(timeout=15) for request in requests) == [201, 422]
    result = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]})
    assert result.status_code == 200
    assert D(result.json()["summary"]["cash"]) == D("20")
    with Session(app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(Transaction)) == 2
        assert db.scalar(select(func.sum(JournalEntry.amount))) == 0


def test_logout_revokes_raw_cookie_and_deactivated_users_cannot_reuse_sessions(client, app):
    old_token = client.cookies.get("hub_session")
    assert client.post("/api/v1/auth/logout").status_code == 204
    with TestClient(
        app, headers={"X-Hub-Request": "1", "Cookie": f"hub_session={old_token}"}
    ) as old:
        assert old.get("/api/v1/auth/session").status_code == 401
        assert old.post("/api/v1/owners", json={"name": "Forbidden"}).status_code == 401
    login = client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}
    )
    assert login.status_code == 200
    new_token = client.cookies.get("hub_session")
    assert new_token != old_token
    with Session(app.state.engine) as db:
        stored = list(db.scalars(select(AuthSession.token_hash)))
        assert stored == [digest(new_token)]
        user = db.scalar(select(User).where(User.email == "admin@example.com"))
        user.active = False
        db.commit()
    assert client.get("/api/v1/dashboard").status_code == 401
    assert client.post("/api/v1/owners", json={"name": "Forbidden"}).status_code == 401


def test_viewer_cannot_use_any_creation_endpoint(client, app, portfolio, instrument):
    payloads = {
        "members": {
            "name": "Injected admin",
            "email": "extra@example.com",
            "password": PASSWORD,
            "role": "admin",
        },
        "owners": {"name": "Injected owner"},
        "portfolios": {
            "name": "Injected",
            "owner_id": portfolio["owner_id"],
            "account_name": "Account",
        },
        "instruments": {"ticker": "EXTRA3", "name": "Injected", "asset_class": "stock"},
        "prices": {
            "instrument_id": instrument["id"],
            "price": "1",
            "as_of": str(today()),
            "source": "Injected",
        },
        "transactions": {
            "portfolio_id": portfolio["id"],
            "event_type": "deposit",
            "gross_amount": "1",
            "trade_date": str(today()),
            "idempotency_key": str(uuid.uuid4()),
        },
    }
    with TestClient(app, headers={"X-Hub-Request": "1"}) as viewer:
        assert (
            viewer.post(
                "/api/v1/auth/login", json={"email": "viewer@example.com", "password": PASSWORD}
            ).status_code
            == 200
        )
        for endpoint, payload in payloads.items():
            response = viewer.post(f"/api/v1/{endpoint}", json=payload)
            assert response.status_code == 403, (endpoint, response.text)
    assert client.get("/api/v1/transactions").json()["total"] == 0


def test_concurrent_failed_logins_cannot_bypass_account_attempt_limit(app):
    def login():
        with TestClient(app, headers={"X-Hub-Request": "1"}) as guest:
            return guest.post(
                "/api/v1/auth/login",
                json={"email": "member@example.com", "password": "wrong-test-password"},
            ).status_code

    with ThreadPoolExecutor(max_workers=4) as pool:
        statuses = list(pool.map(lambda _: login(), range(12)))
    assert sorted(statuses) == [401] * 10 + [429] * 2
    with Session(app.state.engine) as db:
        assert db.scalar(select(LoginAttempt.failures)) == 10
        assert db.scalar(select(func.count()).select_from(AuthSession)) == 0


def test_high_precision_trade_persists_canonical_gross_and_replays(
    client, app, portfolio, instrument
):
    assert record(client, portfolio, "deposit", gross_amount="1").status_code == 201
    assert (
        record(
            client, portfolio, "buy", instrument_id=instrument["id"], quantity="1", unit_price="1"
        ).status_code
        == 201
    )
    quantity = "9999999999.99999999"
    assert (
        record(
            client, portfolio, "split", instrument_id=instrument["id"], quantity=quantity
        ).status_code
        == 201
    )
    sale = record(
        client,
        portfolio,
        "sell",
        instrument_id=instrument["id"],
        quantity=quantity,
        unit_price="9999499999.99999999",
    )
    assert sale.status_code == 201, sale.text
    # Exact product is 99994999999999999800.0050000000000001: round UP, not to the even cent.
    expected = D("99994999999999999800.01")
    assert D(sale.json()["gross_amount"]) == expected
    report = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]})
    assert report.status_code == 200, report.text
    assert D(report.json()["summary"]["cash"]) == expected
    with Session(app.state.engine) as db:
        amounts = dict(
            db.execute(
                select(JournalEntry.account, JournalEntry.amount).where(
                    JournalEntry.transaction_id == sale.json()["id"]
                )
            ).all()
        )
        assert amounts["cash"] == expected
        assert amounts["asset_cost"] == D("-1")


def test_same_day_split_quote_fix_and_export_snapshot_guard(client, portfolio, instrument):
    assert record(client, portfolio, "deposit", gross_amount="1000").status_code == 201
    assert (
        record(
            client,
            portfolio,
            "buy",
            instrument_id=instrument["id"],
            quantity="100",
            unit_price="10",
        ).status_code
        == 201
    )

    def quote(price):
        response = client.post(
            "/api/v1/prices",
            json={
                "instrument_id": instrument["id"],
                "price": price,
                "as_of": str(today()),
                "source": "Review fixture",
            },
        )
        assert response.status_code == 201

    params = {"portfolio_id": portfolio["id"], "as_of": str(today())}
    quote("10")
    before = client.get("/api/v1/dashboard", params=params).json()
    old_export = {**params, "snapshot_id": before["snapshot_id"]}
    assert client.get("/api/v1/reports/positions.csv", params=old_export).status_code == 200
    assert (
        record(client, portfolio, "split", instrument_id=instrument["id"], quantity="2").status_code
        == 201
    )
    report = client.get("/api/v1/dashboard", params=params).json()
    assert report["summary"]["equity"] is None
    changed = client.get("/api/v1/reports/positions.csv", params=old_export)
    assert changed.status_code == 409
    assert changed.json()["error"]["code"] == "SNAPSHOT_CHANGED"
    quote("5")
    fresh = client.get("/api/v1/dashboard", params=params).json()
    assert D(fresh["summary"]["equity"]) == D("1000")
    assert fresh["positions"][0]["quality"] == "valid"
    assert (
        client.get(
            "/api/v1/reports/positions.csv", params={**params, "snapshot_id": fresh["snapshot_id"]}
        ).status_code
        == 200
    )


def test_append_cannot_accept_event_that_breaks_all_subsequent_portfolio_reads(
    client, portfolio, monkeypatch
):
    # Exercise the actual boundary logic without inserting 20,001 test transactions.
    monkeypatch.setattr(portfolio_service, "MAX_EVENTS", 3)
    for _ in range(3):
        assert record(client, portfolio, "deposit", gross_amount="1").status_code == 201
    assert (
        client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).status_code == 200
    )
    overflow = record(client, portfolio, "deposit", gross_amount="1")
    assert overflow.status_code == 422
    assert (
        client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).status_code == 200
    )
