import hashlib
import secrets
from datetime import timedelta

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Request
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from hub_api.errors import AppError
from hub_api.models import AuditEvent, AuthSession, LoginAttempt, User, now

hasher = PasswordHasher()
_dummy_hash = hasher.hash(secrets.token_urlsafe(32))


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def public_user(user: User) -> dict:
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role}


def authenticate(db: Session, email: str, password: str, hours: int) -> tuple[User, str]:
    key = digest(email)
    db.execute(
        insert(LoginAttempt)
        .values(key=key, failures=0, window_start=now())
        .on_conflict_do_nothing()
    )
    attempt = db.scalar(select(LoginAttempt).where(LoginAttempt.key == key).with_for_update())
    assert attempt is not None
    if now() - attempt.window_start > timedelta(minutes=15):
        attempt.failures, attempt.window_start = 0, now()
    if attempt.failures >= 10:
        raise AppError(429, "RATE_LIMIT", "Muitas tentativas. Tente novamente após 15 minutos.")
    user = db.scalar(select(User).where(User.email == email))
    valid = False
    try:
        valid = hasher.verify(user.password_hash if user else _dummy_hash, password)
    except (VerificationError, InvalidHashError):
        pass
    if not user or not user.active or not valid:
        attempt.failures += 1
        db.commit()
        raise AppError(401, "UNAUTHENTICATED", "E-mail ou senha inválidos.")
    attempt.failures = 0
    if hasher.check_needs_rehash(user.password_hash):
        user.password_hash = hasher.hash(password)
    token = secrets.token_urlsafe(48)
    db.add(
        AuthSession(
            token_hash=digest(token), user_id=user.id, expires_at=now() + timedelta(hours=hours)
        )
    )
    db.add(AuditEvent(actor_id=user.id, action="login", entity_type="user", entity_id=user.id))
    db.commit()
    return user, token


def current_user(db: Session, request: Request) -> User:
    token = request.cookies.get("hub_session")
    if not token:
        raise AppError(401, "UNAUTHENTICATED", "Entre para acessar os dados do grupo.")
    user = db.scalar(
        select(User)
        .join(AuthSession, AuthSession.user_id == User.id)
        .where(
            AuthSession.token_hash == digest(token),
            AuthSession.expires_at > now(),
            User.active.is_(True),
        )
    )
    if not user:
        raise AppError(401, "UNAUTHENTICATED", "Sua sessão expirou. Entre novamente.")
    return user


def require_writer(user: User) -> None:
    if user.role not in {"admin", "member"}:
        raise AppError(403, "FORBIDDEN", "Seu acesso é somente para consulta.")


def require_admin(user: User) -> None:
    if user.role != "admin":
        raise AppError(403, "FORBIDDEN", "Esta ação requer um administrador.")
