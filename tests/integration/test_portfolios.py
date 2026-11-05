import csv
import io
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from decimal import Decimal as D

import pytest
from fastapi.testclient import TestClient
from hub_api.models import AuthSession, JournalEntry, Transaction, now
from hub_api.schemas import today
from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

PASSWORD = "test-only-password-123"


def record(client, portfolio, kind, **kwargs):
    return client.post(
        "/api/v1/transactions",
        json={
            "portfolio_id": portfolio["id"],
            "event_type": kind,
            "trade_date": str(today()),
            "idempotency_key": str(uuid.uuid4()),
            **kwargs,
        },
    )


def test_real_persistence_ledger_quotes_and_filtered_export(client, app, portfolio, instrument):
    assert record(client, portfolio, "deposit", gross_amount="10000").status_code == 201
    assert (
        record(
            client,
            portfolio,
            "buy",
            instrument_id=instrument["id"],
            quantity="100",
            unit_price="20",
            fees="10",
        ).status_code
        == 201
    )
    assert (
        record(
            client,
            portfolio,
            "sell",
            instrument_id=instrument["id"],
            quantity="40",
            unit_price="25",
            fees="4",
        ).status_code
        == 201
    )
    result = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).json()
    assert D(result["summary"]["cash"]) == D("8986")
    assert D(result["summary"]["realized_pnl"]) == D("192")
    assert result["summary"]["equity"] is None
    assert result["summary"]["performance"] is None
    assert (
        client.post(
            "/api/v1/prices",
            json={
                "instrument_id": instrument["id"],
                "price": "30",
                "as_of": str(today()),
                "source": "Fixture manual",
            },
        ).status_code
        == 201
    )
    result = client.get("/api/v1/dashboard", params={"portfolio_id": portfolio["id"]}).json()
    assert D(result["summary"]["equity"]) == D("10786")
    assert D(result["positions"][0]["unrealized_pnl"]) == D("594")
    exported = client.get("/api/v1/reports/positions.csv", params={"portfolio_id": portfolio["id"]})
    rows = list(csv.DictReader(io.StringIO(exported.content.decode("utf-8-sig"))))
    assert len(rows) == 1 and D(rows[0]["valor_mercado_brl"]) == D("1800")
    assert rows[0]["snapshot"] == result["snapshot_id"]
    # A new connection sees durable data and balanced postings for every event.
    with Session(app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(Transaction)) == 3
        assert all(
            total == 0
            for total in db.scalars(
                select(func.sum(JournalEntry.amount)).group_by(JournalEntry.transaction_id)
            )
        )


def test_idempotency_and_external_identity(client, portfolio):
    key = str(uuid.uuid4())
    args = {"gross_amount": "100", "idempotency_key": key, "external_id": "statement-row-1"}
    first = record(client, portfolio, "deposit", **args)
    duplicate = record(client, portfolio, "deposit", **args)
    assert first.status_code == 201 and duplicate.status_code == 200
    assert first.json()["id"] == duplicate.json()["id"]
    assert (
        record(client, portfolio, "deposit", **{**args, "gross_amount": "101"}).status_code == 409
    )
    other_file = record(
        client, portfolio, "deposit", **{**args, "idempotency_key": str(uuid.uuid4())}
    )
    assert other_file.status_code == 200 and other_file.json()["id"] == first.json()["id"]
    assert D(client.get("/api/v1/dashboard").json()["summary"]["cash"]) == D("100")


def test_concurrent_retries_have_one_effect(client, app, portfolio):
    cookie = client.cookies.get("hub_session")
    payload = {
        "portfolio_id": portfolio["id"],
        "event_type": "deposit",
        "gross_amount": "100",
        "trade_date": str(today()),
        "idempotency_key": str(uuid.uuid4()),
    }

    def post():
        with TestClient(
            app, headers={"X-Hub-Request": "1", "Cookie": f"hub_session={cookie}"}
        ) as other:
            response = other.post("/api/v1/transactions", json=payload)
            return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: post(), range(4)))
    assert sorted(status for status, _ in responses) == [200, 200, 200, 201]
    assert len({body["id"] for _, body in responses}) == 1
    assert D(client.get("/api/v1/dashboard").json()["summary"]["cash"]) == D("100")


def test_roles_shared_group_and_external_access(client, app, portfolio):
    assert record(client, portfolio, "deposit", gross_amount="100").status_code == 201
    with TestClient(app, headers={"X-Hub-Request": "1"}) as other:
        assert other.get("/api/v1/dashboard").status_code == 401
        login = other.post(
            "/api/v1/auth/login", json={"email": "member@example.com", "password": PASSWORD}
        )
        assert login.status_code == 200 and "HttpOnly" in login.headers["set-cookie"]
        assert D(other.get("/api/v1/dashboard").json()["summary"]["cash"]) == D("100")
        assert (
            other.post(
                "/api/v1/members",
                json={
                    "email": "new@example.com",
                    "name": "Test",
                    "password": PASSWORD,
                    "role": "admin",
                },
            ).status_code
            == 403
        )
        other.post("/api/v1/auth/logout")
        assert other.get("/api/v1/auth/session").status_code == 401
        other.post("/api/v1/auth/login", json={"email": "viewer@example.com", "password": PASSWORD})
        assert other.get("/api/v1/dashboard").status_code == 200
        assert record(other, portfolio, "deposit", gross_amount="1").status_code == 403


def test_csrf_expiry_validation_and_no_secret_echo(client, app):
    assert (
        client.post(
            "/api/v1/owners", json={"name": "Evil"}, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    with TestClient(app) as other:
        assert (
            other.post(
                "/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}
            ).status_code
            == 403
        )
    response = client.post(
        "/api/v1/members", json={"name": "X", "email": "bad", "password": "secret"}
    )
    assert response.status_code == 422 and "secret" not in response.text
    with Session(app.state.engine) as db:
        for session in db.scalars(select(AuthSession)):
            session.expires_at = now() - timedelta(hours=1)
        db.commit()
    assert client.get("/api/v1/dashboard").status_code == 401


def test_insufficient_cash_rollback_and_immutable_storage(client, app, portfolio, instrument):
    response = record(
        client, portfolio, "buy", instrument_id=instrument["id"], quantity="1", unit_price="20"
    )
    assert response.status_code == 422
    assert record(client, portfolio, "deposit", gross_amount="100").status_code == 201
    with Session(app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(Transaction)) == 1
        for table in ("transactions", "journal_entries", "audit_events"):
            with pytest.raises(DBAPIError):
                db.execute(text(f"DELETE FROM {table}"))
                db.commit()
            db.rollback()
    assert D(client.get("/api/v1/dashboard").json()["summary"]["cash"]) == D("100")


def test_history_asof_ownership_and_quote_age(client, portfolio, instrument):
    earlier = today() - timedelta(days=15)
    assert (
        record(
            client, portfolio, "deposit", gross_amount="100", trade_date=str(earlier)
        ).status_code
        == 201
    )
    assert (
        record(
            client,
            portfolio,
            "buy",
            instrument_id=instrument["id"],
            quantity="2",
            unit_price="10",
            trade_date=str(earlier),
        ).status_code
        == 201
    )
    client.post(
        "/api/v1/prices",
        json={
            "instrument_id": instrument["id"],
            "price": "12",
            "as_of": str(earlier),
            "source": "Teste",
        },
    )
    assert client.get("/api/v1/dashboard").json()["positions"][0]["quality"] == "stale"
    assert (
        record(client, portfolio, "split", instrument_id=instrument["id"], quantity="2").status_code
        == 201
    )
    result = client.get("/api/v1/dashboard").json()
    assert (
        result["summary"]["equity"] is None
    )  # never multiply a pre-split quote by post-split quantity
    assert D(result["positions"][0]["quantity"]) == 4
    historical = client.get("/api/v1/dashboard", params={"as_of": str(earlier)}).json()
    assert D(historical["summary"]["equity"]) == 104
    assert (
        record(
            client, portfolio, "withdrawal", gross_amount="1", trade_date=str(earlier)
        ).status_code
        == 409
    )
    assert (
        client.get(
            "/api/v1/dashboard", params={"as_of": str(today() + timedelta(days=1))}
        ).status_code
        == 422
    )


def test_filtered_export_excludes_other_owner(client, portfolio, instrument):
    owner = client.post("/api/v1/owners", json={"name": "Segundo titular"}).json()
    second = client.post(
        "/api/v1/portfolios",
        json={"name": "Segunda", "owner_id": owner["id"], "account_name": "Conta"},
    ).json()
    for p, amount in [(portfolio, "100"), (second, "200")]:
        record(client, p, "deposit", gross_amount=amount)
        record(client, p, "buy", instrument_id=instrument["id"], quantity="1", unit_price="10")
    filtered = client.get("/api/v1/dashboard", params={"owner_id": owner["id"]}).json()
    assert D(filtered["summary"]["net_contributions"]) == 200
    assert len(filtered["positions"]) == 1
    csv_data = client.get("/api/v1/reports/positions.csv", params={"owner_id": owner["id"]}).text
    assert "Segundo titular" in csv_data and "Titular de teste" not in csv_data
