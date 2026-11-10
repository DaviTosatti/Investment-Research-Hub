import uuid

from hub_api.schemas import today


def test_money_inputs_reject_binary_json_numbers(client, portfolio):
    payload = {
        "portfolio_id": portfolio["id"],
        "event_type": "deposit",
        "trade_date": str(today()),
        "idempotency_key": str(uuid.uuid4()),
    }
    for amount in (100, 100.1):
        response = client.post("/api/v1/transactions", json={**payload, "gross_amount": amount})
        assert response.status_code == 422
    response = client.post("/api/v1/transactions", json={**payload, "gross_amount": "100.10"})
    assert response.status_code == 201
    assert isinstance(response.json()["gross_amount"], str)


def test_openapi_response_contracts_are_available_only_to_members(client, app):
    from fastapi.testclient import TestClient

    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "DashboardRead" in schema["components"]["schemas"]
    assert "TransactionRead" in schema["components"]["schemas"]
    with TestClient(app) as guest:
        assert guest.get("/api/v1/openapi.json").status_code == 401
