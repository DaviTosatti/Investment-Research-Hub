import hashlib
import uuid
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from hub_api.schemas import today
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

DAY = "2026-01-05"
HEADER = "event_type;trade_date;gross_amount;external_id\n"
CONFIG = {"mapping": {name: name for name in HEADER.strip().split(";")}}


def source(client, name="Extrato sintético"):
    response = client.post("/api/v1/sources", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def upload(client, portfolio, source_id, content, filename="extrato.csv", **options):
    response = client.post(
        "/api/v1/imports",
        params={
            "portfolio_id": portfolio["id"],
            "source_id": source_id,
            "filename": filename,
            **options,
        },
        content=content,
        headers={"Content-Type": "application/octet-stream"},
    )
    assert response.status_code in (200, 201), response.text
    return response.json()


def preview(client, batch, config=None):
    response = client.post(f"/api/v1/imports/{batch['id']}/preview", json=config or CONFIG)
    assert response.status_code == 201, response.text
    return response.json()


def confirm(client, batch, snapshot):
    return client.post(
        f"/api/v1/imports/{batch['id']}/confirm", json={"preview_id": snapshot["id"]}
    )


def test_original_preview_receipt_lineage_and_cross_file_reimport(client, portfolio):
    origin = source(client)
    content = (HEADER + f"deposit;{DAY};100.10;A1\nwithdrawal;{DAY};20.05;W1\n").encode()
    batch = upload(client, portfolio, origin, content)
    assert batch["sha256"] == hashlib.sha256(content).hexdigest()
    assert client.get(batch["original_url"]).content == content
    snapshot = preview(client, batch)
    assert snapshot["summary"]["ready"] == 2
    assert snapshot["summary"]["cash_after"] == "80.05"
    assert client.get("/api/v1/transactions").json()["total"] == 0
    result = confirm(client, batch, snapshot)
    assert result.status_code == 201, result.text
    assert confirm(client, batch, snapshot).json() == result.json()
    assert upload(client, portfolio, origin, content)["id"] == batch["id"]
    # Different bytes and filename, equal source IDs: both recognized, neither re-posted.
    other = upload(client, portfolio, origin, content.replace(b"100.10", b"100.100"), "outro.csv")
    other_preview = preview(client, other)
    assert other_preview["summary"]["duplicate"] == 2
    assert confirm(client, other, other_preview).status_code == 201
    assert client.get("/api/v1/transactions").json()["total"] == 2
    assert Decimal(client.get("/api/v1/dashboard").json()["summary"]["cash"]) == Decimal("80.05")
    lineage = client.get("/api/v1/lineage", params={"import_id": batch["id"]}).json()
    assert lineage["owner_id"] == portfolio["owner_id"]
    assert lineage["receipt"]["results"] == result.json()["results"]
    frozen = client.get(f"/api/v1/snapshots/{snapshot['id']}").json()
    assert frozen == snapshot
    assert client.get("/api/v1/quality").json()["total"] == 2


def test_nulls_quarantine_traceable_edit_and_old_preview_refusal(client, portfolio):
    batch = upload(client, portfolio, source(client), (HEADER + f"deposit;{DAY};;A1\n").encode())
    old = preview(client, batch)
    assert old["rows"][0]["raw"]["gross_amount"] is None
    assert old["summary"]["quarantined"] == 1
    assert confirm(client, batch, old).status_code == 422
    fixed = preview(
        client,
        batch,
        {
            **CONFIG,
            "edits": [
                {
                    "row_number": 2,
                    "values": {"gross_amount": "125.25"},
                    "reason": "Valor conferido no documento original de teste",
                }
            ],
        },
    )
    assert fixed["revision"] == 2
    assert fixed["rows"][0]["raw"]["gross_amount"] is None
    assert fixed["summary"]["cash_after"] == "125.25"
    assert client.get(f"/api/v1/snapshots/{old['id']}").json() == old
    assert confirm(client, batch, old).status_code == 409
    assert confirm(client, batch, fixed).status_code == 201
    assert client.get("/api/v1/snapshots", params={"import_id": batch["id"]}).json()["total"] == 2


def test_ambiguous_duplicates_require_decision_but_distinct_execution_ids_do_not(client, portfolio):
    src = source(client)
    content = (HEADER + f"deposit;{DAY};100;\ndeposit;{DAY};100;\n").encode()
    batch = upload(client, portfolio, src, content)
    first = preview(client, batch)
    assert first["summary"]["needs_review"] == 1
    assert confirm(client, batch, first).status_code == 422
    fixed = preview(
        client,
        batch,
        {
            **CONFIG,
            "decisions": [
                {
                    "row_number": 3,
                    "action": "create",
                    "reason": "Segundo aporte real, conferido no extrato",
                }
            ],
        },
    )
    assert fixed["summary"]["cash_after"] == "200"
    assert confirm(client, batch, fixed).status_code == 201
    # A new source/external ID cannot evade reconciliation against a manual or unnumbered event.
    other = upload(
        client,
        portfolio,
        source(client, "Outra origem"),
        (HEADER + f"deposit;{DAY};100;new-id\n").encode(),
    )
    assert preview(client, other)["summary"]["needs_review"] == 1


def test_repeated_same_id_within_file_and_conflicting_value(client, portfolio):
    batch = upload(
        client,
        portfolio,
        source(client),
        (HEADER + f"deposit;{DAY};100;A1\ndeposit;{DAY};100;A1\ndeposit;{DAY};200;A1\n").encode(),
    )
    first = preview(client, batch)
    assert first["summary"]["ready"] == 1
    assert first["summary"]["duplicate"] == 1
    assert first["summary"]["quarantined"] == 1
    resolved = preview(
        client,
        batch,
        {
            **CONFIG,
            "decisions": [
                {
                    "row_number": 4,
                    "action": "skip",
                    "reason": "Linha divergente; documento será revisado",
                }
            ],
        },
    )
    result = confirm(client, batch, resolved)
    assert result.status_code == 201, result.text
    rows = result.json()["results"]
    assert rows[0]["transaction_id"] == rows[1]["transaction_id"]
    assert rows[2]["transaction_id"] is None


def test_stale_preview_concurrent_imports_never_duplicate(client, app, portfolio):
    src = source(client)
    first = upload(client, portfolio, src, (HEADER + f"deposit;{DAY};100;A1\n").encode())
    second = upload(client, portfolio, src, (HEADER + f"deposit;{DAY};100.0;A1\n").encode())
    pairs = [(first, preview(client, first)), (second, preview(client, second))]
    cookies = dict(client.cookies)

    def post(pair):
        with TestClient(app, cookies=cookies, headers={"X-Hub-Request": "1"}) as concurrent:
            return confirm(concurrent, *pair)

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(post, pairs))
    assert sorted(r.status_code for r in responses) == [201, 409]
    failed = pairs[next(i for i, r in enumerate(responses) if r.status_code == 409)][0]
    retry = preview(client, failed)
    assert retry["summary"]["duplicate"] == 1
    assert confirm(client, failed, retry).status_code == 201
    assert client.get("/api/v1/transactions").json()["total"] == 1
    with ThreadPoolExecutor(max_workers=2) as pool:
        same = list(pool.map(post, [(failed, retry)] * 2))
    assert [r.status_code for r in same] == [200, 200]


def test_decimal_units_chronology_and_canonical_buy(client, portfolio, instrument):
    src = source(client)
    body = (
        "tipo;data;valor;quantidade;preco;ticker;moeda;referencia\n"
        f"aporte;05/01/2026;100,00;0;0;;BRL;D1\n"
        f"compra;06/01/2026;30,03;3;10,01;{instrument['ticker']};BRL;B1\n"
    ).encode()
    batch = upload(client, portfolio, src, body)
    config = {
        "mapping": dict(
            zip(
                [
                    "event_type",
                    "trade_date",
                    "gross_amount",
                    "quantity",
                    "unit_price",
                    "ticker",
                    "currency",
                    "external_id",
                ],
                ["tipo", "data", "valor", "quantidade", "preco", "ticker", "moeda", "referencia"],
                strict=True,
            )
        ),
        "date_format": "DD/MM/YYYY",
        "decimal_separator": ",",
        "exchange": "TEST",
    }
    snap = preview(client, batch, config)
    assert snap["summary"]["can_commit"], snap
    assert snap["summary"]["cash_after"] == "69.97"
    assert snap["summary"]["period_end"] == "2026-01-06"
    assert confirm(client, batch, snap).status_code == 201
    dashboard = client.get("/api/v1/dashboard").json()
    assert Decimal(dashboard["positions"][0]["quantity"]) == Decimal("3")
    assert Decimal(dashboard["positions"][0]["cost_basis"]) == Decimal("30.03")
    older = upload(client, portfolio, src, (HEADER + "deposit;2026-01-01;1;older\n").encode())
    assert preview(client, older)["summary"]["quarantined"] == 1


def test_current_ledger_change_and_invalid_batch_have_no_partial_writes(client, portfolio):
    batch = upload(
        client,
        portfolio,
        source(client),
        (HEADER + f"deposit;{DAY};100;A1\nwithdrawal;{DAY};200;W1\n").encode(),
    )
    snap = preview(client, batch)
    assert snap["summary"]["quarantined"] == 1
    assert confirm(client, batch, snap).status_code == 422
    assert client.get("/api/v1/transactions").json()["total"] == 0
    fixed = preview(
        client,
        batch,
        {
            **CONFIG,
            "edits": [
                {
                    "row_number": 3,
                    "values": {"gross_amount": "20"},
                    "reason": "Correção comprovada no extrato",
                }
            ],
        },
    )
    assert (
        client.post(
            "/api/v1/transactions",
            json={
                "portfolio_id": portfolio["id"],
                "event_type": "deposit",
                "gross_amount": "1",
                "trade_date": str(today()),
                "idempotency_key": str(uuid.uuid4()),
            },
        ).status_code
        == 201
    )
    assert confirm(client, batch, fixed).json()["error"]["code"] == "STALE_PREVIEW"
    assert client.get("/api/v1/transactions").json()["total"] == 1


def test_original_and_revision_immutability_permissions_and_limits(client, app, portfolio):
    src = source(client)
    batch = upload(client, portfolio, src, (HEADER + f"deposit;{DAY};100;A1\n").encode())
    snap = preview(client, batch)
    with app.state.engine.connect() as conn:
        for table in ("original_files", "import_batches", "import_previews", "data_sources"):
            with pytest.raises(DBAPIError):
                conn.execute(text(f"DELETE FROM {table}"))
            conn.rollback()
    with TestClient(app, headers={"X-Hub-Request": "1"}) as viewer:
        assert viewer.get(batch["original_url"]).status_code == 401
        viewer.post(
            "/api/v1/auth/login",
            json={"email": "viewer@example.com", "password": "test-only-password-123"},
        )
        assert viewer.get(batch["original_url"]).status_code == 200
        assert viewer.post("/api/v1/sources", json={"name": "Fonte"}).status_code == 403
        assert confirm(viewer, batch, snap).status_code == 403
        assert viewer.post(f"/api/v1/imports/{batch['id']}/preview", json=CONFIG).status_code == 403
    oversized = client.post(
        "/api/v1/imports",
        params={
            "portfolio_id": portfolio["id"],
            "source_id": src,
            "filename": "big.csv",
        },
        content=b"x" * (2 * 1024 * 1024 + 1),
    )
    assert oversized.status_code == 413
    for path in ("/sources", "/imports", "/snapshots", "/quality", "/lineage"):
        assert "/api/v1" + path in client.get("/api/v1/openapi.json").json()["paths"]


def test_distinct_provider_ids_preserve_real_identical_deposits(client, portfolio):
    batch = upload(
        client,
        portfolio,
        source(client),
        (HEADER + f"deposit;{DAY};100;A1\ndeposit;{DAY};100;A2\n").encode(),
    )
    snap = preview(client, batch)
    assert snap["summary"]["ready"] == 2
    assert confirm(client, batch, snap).status_code == 201
    assert client.get("/api/v1/transactions").json()["total"] == 2


def test_failed_commit_rolls_back_events_journal_and_receipt(client, app, portfolio, monkeypatch):
    from hub_api import import_service
    from hub_api.errors import AppError

    batch = upload(
        client,
        portfolio,
        source(client),
        (HEADER + f"deposit;{DAY};100;A1\ndeposit;{DAY};20;A2\n").encode(),
    )
    snap = preview(client, batch)
    append = import_service.append_event
    calls = 0

    def interrupted(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise AppError(503, "SIMULATED_FAILURE", "Falha sintética antes do commit.")
        return append(*args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(import_service, "append_event", interrupted)
        assert confirm(client, batch, snap).status_code == 503
    with app.state.engine.connect() as conn:
        for table in ("transactions", "journal_entries", "import_receipts"):
            assert conn.scalar(text(f"SELECT count(*) FROM {table}")) == 0
    assert confirm(client, batch, snap).status_code == 201


def test_same_original_is_deduplicated_without_mixing_owners(client, app, portfolio):
    src = source(client)
    owner = client.post("/api/v1/owners", json={"name": "Segundo titular sintético"}).json()
    second = client.post(
        "/api/v1/portfolios",
        json={
            "owner_id": owner["id"],
            "name": "Segunda carteira",
            "account_name": "Outra conta",
        },
    ).json()
    original = (HEADER + f"deposit;{DAY};50;A1\n").encode()
    cookies = dict(client.cookies)

    def receive(target):
        with TestClient(app, cookies=cookies, headers={"X-Hub-Request": "1"}) as parallel:
            return upload(parallel, target, src, original)

    with ThreadPoolExecutor(max_workers=2) as pool:
        batches = list(pool.map(receive, [portfolio, second]))
    assert batches[0]["id"] != batches[1]["id"]
    assert batches[0]["owner_id"] != batches[1]["owner_id"]
    for batch in batches:
        assert confirm(client, batch, preview(client, batch)).status_code == 201
    with app.state.engine.connect() as conn:
        assert conn.scalar(text("SELECT count(*) FROM original_files")) == 1
    for target in (portfolio, second):
        dashboard = client.get("/api/v1/dashboard", params={"portfolio_id": target["id"]}).json()
        assert Decimal(dashboard["summary"]["cash"]) == Decimal("50")
