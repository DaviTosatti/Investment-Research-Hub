from unittest.mock import patch

import pytest
from hub_api.cli import create_admin, needs_first_admin, prompt_first_admin
from hub_api.models import AuditEvent, User
from hub_api.schemas import MemberCreate
from hub_api.security import hasher
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session


def test_existing_admin_is_preserved_without_any_prompt(app):
    url = app.state.engine.url.render_as_string(hide_password=False)
    with Session(app.state.engine) as db:
        before = db.scalar(select(User.password_hash).where(User.email == "admin@example.com"))
    with patch("builtins.input", side_effect=AssertionError("must not prompt")), patch(
        "getpass.getpass", side_effect=AssertionError("must not prompt")
    ):
        prompt_first_admin(url)
    with Session(app.state.engine) as db:
        assert db.scalar(select(User.password_hash).where(User.email == "admin@example.com")) == before
        assert db.scalar(select(func.count()).select_from(User)) == 3


def test_first_admin_validates_without_echoing_password_and_records_audit(app, capsys):
    url = app.state.engine.url.render_as_string(hide_password=False)
    with app.state.engine.begin() as connection:
        connection.execute(text("TRUNCATE users CASCADE"))
    assert needs_first_admin(url)
    with patch("builtins.input", side_effect=["bad-address", "Nome", "local@example.com", "João"]), patch(
        "getpass.getpass", side_effect=["bad-pass", "bad-pass", "private-password-123", "private-password-123"]
    ):
        prompt_first_admin(url)
    output = capsys.readouterr().out
    assert "bad-pass" not in output and "private-password-123" not in output
    assert "E-mail inválido" in output
    assert "Senha muito curta" in output and "8 caracteres" in output and "mínimo é 12" in output
    assert not needs_first_admin(url)
    with Session(app.state.engine) as db:
        user = db.scalar(select(User))
        assert user.name == "João" and user.role == "admin"
        assert hasher.verify(user.password_hash, "private-password-123")
        assert db.scalar(select(AuditEvent.action).where(AuditEvent.entity_id == user.id)) == "bootstrap"
    with pytest.raises(ValueError, match="Já existe"):
        create_admin(url, MemberCreate(email="local@example.com", name="Other", password="different-password"))


def test_password_confirmation_error_explains_the_failure_without_echoing_secrets(app, capsys):
    url = app.state.engine.url.render_as_string(hide_password=False)
    with app.state.engine.begin() as connection:
        connection.execute(text("TRUNCATE users CASCADE"))
    with patch("builtins.input", side_effect=["test@example.com", "Nome", KeyboardInterrupt]), patch(
        "getpass.getpass", side_effect=["synthetic-password-one", "synthetic-password-two"]
    ), pytest.raises(KeyboardInterrupt):
        prompt_first_admin(url)
    output = capsys.readouterr().out
    assert "Cadastro não concluído: a confirmação da senha é diferente" in output
    assert "synthetic-password" not in output
    assert needs_first_admin(url)


@pytest.mark.parametrize("payload, expected", [
    ({"email": "invalid-email", "password": "synthetic-password"}, "E-mail inválido"),
    ({"email": "test@example.com", "password": ""}, "Informe a senha."),
    ({"email": "test@example.com", "password": "x" * 129}, "Senha muito longa. O máximo é 128"),
])
def test_login_validation_explains_each_error_without_exposing_credentials(client, payload, expected):
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert expected in response.json()["error"]["message"]
    assert payload["email"] not in response.text
    if payload["password"]:
        assert payload["password"] not in response.text


def test_invalid_login_credentials_report_the_failure_without_creating_an_account(client, app):
    with Session(app.state.engine) as db:
        users_before = db.scalar(select(func.count()).select_from(User))
    for email in ("admin@example.com", "absent@example.com"):
        response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-synthetic-password"})
        assert response.status_code == 401
        assert response.json()["error"]["message"] == "E-mail ou senha inválidos."
        assert "set-cookie" not in response.headers
    with Session(app.state.engine) as db:
        assert db.scalar(select(func.count()).select_from(User)) == users_before


def test_setup_does_not_reactivate_existing_disabled_admin(app):
    url = app.state.engine.url.render_as_string(hide_password=False)
    with Session(app.state.engine) as db:
        user = db.scalar(select(User).where(User.role == "admin"))
        user.active = False
        db.commit()
    with pytest.raises(ValueError, match="existentes"):
        needs_first_admin(url)


def test_first_access_displays_each_field_before_waiting_for_input(app, capsys):
    url = app.state.engine.url.render_as_string(hide_password=False)
    with app.state.engine.begin() as connection:
        connection.execute(text("TRUNCATE users CASCADE"))
    fields = iter([("E-mail:\n", "prompt@example.com"), ("Nome:\n", "Nome visível")])

    def enter_value():
        label, value = next(fields)
        assert label in capsys.readouterr().out
        return value

    with patch("builtins.input", side_effect=enter_value), patch(
        "getpass.getpass", return_value="test-only-private-password"
    ):
        prompt_first_admin(url)
    assert not needs_first_admin(url)
