"""Local administration; passwords are read from a hidden prompt, never arguments."""

import argparse
import getpass

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from hub_api.config import get_settings
from hub_api.models import AuditEvent, User
from hub_api.schemas import MemberCreate
from hub_api.security import hasher


def main():
    parser = argparse.ArgumentParser(description="Administração local do Investment Research Hub")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser(
        "create-admin", help="Criar administrador com senha lida de forma privada"
    )
    create.add_argument("--email", required=True)
    create.add_argument("--name", required=True)
    args = parser.parse_args()
    password = getpass.getpass("Senha (mínimo 12 caracteres): ")
    if password != getpass.getpass("Repita a senha: "):
        parser.error("As senhas não coincidem.")
    payload = MemberCreate(email=args.email, name=args.name, password=password, role="admin")
    engine = create_engine(get_settings().database_url)
    with Session(engine) as db:
        if db.scalar(select(User).where(User.email == str(payload.email))):
            parser.error("Já existe um usuário com este e-mail.")
        user = User(
            name=payload.name,
            email=str(payload.email),
            role="admin",
            password_hash=hasher.hash(payload.password),
        )
        db.add(user)
        db.flush()
        db.add(
            AuditEvent(actor_id=user.id, action="bootstrap", entity_type="user", entity_id=user.id)
        )
        db.commit()
    engine.dispose()
    print("Administrador criado. Acesse a interface para entrar.")


if __name__ == "__main__":
    main()
