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
        "getpass.getpass", side_effect=["bad-secret", "bad-secret", "private-password-123", "private-password-123"]
    ):
        prompt_first_admin(url)
    output = capsys.readouterr().out
    assert "bad-secret" not in output and "private-password-123" not in output
    assert not needs_first_admin(url)
    with Session(app.state.engine) as db:
        user = db.scalar(select(User))
        assert user.name == "João" and user.role == "admin"
        assert hasher.verify(user.password_hash, "private-password-123")
        assert db.scalar(select(AuditEvent.action).where(AuditEvent.entity_id == user.id)) == "bootstrap"
    with pytest.raises(ValueError, match="Já existe"):
        create_admin(url, MemberCreate(email="local@example.com", name="Other", password="different-password"))


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
