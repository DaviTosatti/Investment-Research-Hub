import uuid
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from hub_api.config import Settings
from hub_api.main import create_app
from hub_api.models import Base, User
from hub_api.security import hasher
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

PASSWORD = "test-only-password-123"


@pytest.fixture(scope="session")
def database_url():
    base_url = make_url(Settings().database_url)
    name = "hub_test_" + uuid.uuid4().hex
    admin = create_engine(base_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    url = base_url.set(database=name).render_as_string(hide_password=False)
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    command.upgrade(config, "head")
    yield url
    with admin.connect() as conn:
        conn.execute(text(f'DROP DATABASE "{name}" WITH (FORCE)'))
    admin.dispose()


@pytest.fixture
def app(database_url):
    app = create_app(Settings(database_url=database_url, public_origin="http://testserver"))
    with app.state.engine.begin() as conn:
        names = ", ".join('"' + t.name + '"' for t in Base.metadata.sorted_tables)
        conn.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    with Session(app.state.engine) as db:
        for role in ("admin", "member", "viewer"):
            db.add(
                User(
                    name=f"Test {role}",
                    email=f"{role}@example.com",
                    role=role,
                    password_hash=hasher.hash(PASSWORD),
                )
            )
        db.commit()
    yield app
    app.state.engine.dispose()


@pytest.fixture
def client(app):
    with TestClient(app, headers={"X-Hub-Request": "1", "Origin": "http://testserver"}) as client:
        response = client.post(
            "/api/v1/auth/login", json={"email": "admin@example.com", "password": PASSWORD}
        )
        assert response.status_code == 200
        yield client


@pytest.fixture
def portfolio(client):
    owner = client.post("/api/v1/owners", json={"name": "Titular de teste"}).json()
    response = client.post(
        "/api/v1/portfolios",
        json={
            "name": "Carteira de teste",
            "owner_id": owner["id"],
            "account_name": "Conta de teste",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def instrument(client):
    response = client.post(
        "/api/v1/instruments",
        json={
            "ticker": "TEST3",
            "name": "Ativo sintético",
            "asset_class": "stock",
            "exchange": "TEST",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()
