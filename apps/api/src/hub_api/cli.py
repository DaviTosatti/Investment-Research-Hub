"""Local administration; passwords are read from a hidden prompt, never arguments."""

import argparse
import getpass

from pydantic import ValidationError
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from hub_api.config import get_settings
from hub_api.errors import account_validation_message
from hub_api.models import AuditEvent, User
from hub_api.schemas import MemberCreate
from hub_api.security import hasher


def create_admin(database_url, payload):
    engine = create_engine(database_url)
    try:
        with Session(engine) as db:
            if db.scalar(select(User).where(User.email == str(payload.email))):
                raise ValueError("Já existe um usuário com este e-mail.")
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
    finally:
        engine.dispose()


def needs_first_admin(database_url):
    engine = create_engine(database_url)
    try:
        with Session(engine) as db:
            if db.scalar(select(User.id).where(User.role == "admin", User.active).limit(1)):
                return False
            if db.scalar(select(func.count()).select_from(User)):
                raise ValueError("Há usuários existentes sem administrador ativo. Use create-admin.")
            return True
    finally:
        engine.dispose()


def prompt_first_admin(database_url):
    if not needs_first_admin(database_url):
        return
    print("\nPrimeiro acesso: crie sua conta de administrador.", flush=True)
    print("Digite cada campo e pressione Enter. A senha fica oculta durante a digitação.", flush=True)
    while True:
        # Complete lines remain visible even through a line-buffered console host.
        print("E-mail:", flush=True)
        email = input().strip()
        print("Nome:", flush=True)
        name = input().strip()
        password = getpass.getpass("Senha (mínimo 12 caracteres; não aparece na tela): ")
        if password != getpass.getpass("Repita a senha: "):
            print("Cadastro não concluído: a confirmação da senha é diferente. Digite a mesma senha nos dois campos.", flush=True)
            continue
        try:
            payload = MemberCreate(email=email, name=name, password=password, role="admin")
        except ValidationError as error:
            message = account_validation_message(
                error.errors(include_input=False), password_length=len(password.strip())
            )
            print(f"Cadastro não concluído: {message}", flush=True)
            continue
        create_admin(database_url, payload)
        print("Administrador criado. Use essa conta para entrar no navegador.")
        return


def main():
    parser = argparse.ArgumentParser(description="Administração local do Investment Research Hub")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-admin", help="Criar administrador com senha privada")
    create.add_argument("--email", required=True)
    create.add_argument("--name", required=True)
    commands.add_parser("setup-admin", help="Criar interativamente o primeiro administrador")
    args = parser.parse_args()
    if args.command == "setup-admin":
        try:
            prompt_first_admin(get_settings().database_url)
        except ValueError as error:
            parser.error(str(error))
        return
    password = getpass.getpass("Senha (mínimo 12 caracteres): ")
    if password != getpass.getpass("Repita a senha: "):
        parser.error("As senhas não coincidem.")
    try:
        payload = MemberCreate(email=args.email, name=args.name, password=password, role="admin")
        create_admin(get_settings().database_url, payload)
    except ValidationError as error:
        parser.error(account_validation_message(
            error.errors(include_input=False), password_length=len(password.strip())
        ))
    except ValueError as error:
        parser.error(str(error))
    print("Administrador criado. Acesse a interface para entrar.")


if __name__ == "__main__":
    main()
