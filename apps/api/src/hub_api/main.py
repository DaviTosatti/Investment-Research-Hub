import csv
import hashlib
import io
import json
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from hub_finance.ledger import Event, LedgerError, apply_event, decimal_string, event_gross
from sqlalchemy import create_engine, delete, func, select, text
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from hub_api.config import Settings, get_settings
from hub_api.errors import AppError
from hub_api.models import (
    Account,
    AuditEvent,
    AuthSession,
    Instrument,
    Issuer,
    JournalEntry,
    Listing,
    Owner,
    Portfolio,
    Price,
    Transaction,
    User,
)
from hub_api.portfolio_service import dashboard, event_rows, replay
from hub_api.responses import (
    AuditRead,
    AuthRead,
    DashboardRead,
    InstrumentRead,
    OwnerRead,
    Page,
    PortfolioRead,
    PriceRead,
    TransactionRead,
    UserRead,
)
from hub_api.schemas import (
    InstrumentCreate,
    Login,
    MemberCreate,
    OwnerCreate,
    PortfolioCreate,
    PriceCreate,
    TransactionCreate,
    today,
)
from hub_api.security import (
    authenticate,
    current_user,
    digest,
    hasher,
    public_user,
    require_admin,
    require_writer,
)

logger = logging.getLogger("hub.requests")


def get_db(request: Request):
    with request.app.state.session_factory() as db:
        yield db


DB = Annotated[Session, Depends(get_db)]


def get_user(request: Request, db: DB) -> User:
    return current_user(db, request)


Actor = Annotated[User, Depends(get_user)]
Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]


def page(items: list, total: int, limit: int, offset: int) -> dict:
    return {"items": items, "total": total, "limit": limit, "offset": offset}


def audit(db: Session, actor: User, action: str, entity: str, entity_id: str) -> None:
    db.add(AuditEvent(actor_id=actor.id, action=action, entity_type=entity, entity_id=entity_id))


def need(db: Session, model, identifier):
    value = db.get(model, str(identifier))
    if not value:
        raise AppError(404, "NOT_FOUND", "Registro não encontrado.")
    return value


def portfolio_item(db: Session, row: Portfolio) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "owner_id": row.owner_id,
        "owner_name": need(db, Owner, row.owner_id).name,
        "account_name": need(db, Account, row.account_id).name,
        "currency": row.currency,
        "created_at": row.created_at.isoformat(),
    }


def transaction_item(db: Session, row: Transaction) -> dict:
    portfolio = need(db, Portfolio, row.portfolio_id)
    return {
        "id": row.id,
        "portfolio_id": row.portfolio_id,
        "portfolio_name": portfolio.name,
        "owner_name": need(db, Owner, row.owner_id).name,
        "instrument_id": row.instrument_id,
        "ticker": db.scalar(
            select(Listing.ticker).where(Listing.instrument_id == row.instrument_id)
        )
        if row.instrument_id
        else None,
        "event_type": row.event_type,
        "quantity": decimal_string(row.quantity),
        "unit_price": decimal_string(row.unit_price),
        "gross_amount": decimal_string(row.gross_amount),
        "fees": decimal_string(row.fees),
        "taxes": decimal_string(row.taxes),
        "trade_date": row.trade_date.isoformat(),
        "settlement_date": row.settlement_date.isoformat(),
        "source": row.source,
        "external_id": row.external_id,
        "notes": row.notes,
        "created_by": row.created_by,
        "created_at": row.created_at.isoformat(),
        "revision": row.revision,
    }


def canonical_hash(payload: TransactionCreate) -> str:
    values = payload.model_dump(mode="json", exclude={"idempotency_key"})
    # Numerically equal decimal strings (10, 10.0) represent the same intent.
    for key in ("quantity", "unit_price", "gross_amount", "fees", "taxes"):
        values[key] = format(getattr(payload, key).normalize(), "f")
    return hashlib.sha256(
        json.dumps(values, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    engine = create_engine(
        settings.database_url, pool_pre_ping=True, connect_args={"options": "-c timezone=UTC"}
    )

    @asynccontextmanager
    async def lifespan(app):
        yield
        engine.dispose()

    app = FastAPI(
        title="Investment Research Hub",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.engine = engine
    app.state.session_factory = sessionmaker(engine, expire_on_commit=False)

    @app.middleware("http")
    async def protect(request: Request, call_next):
        request_id, started = str(uuid.uuid4()), time.monotonic()
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if request.headers.get("x-hub-request") != "1" or (
                origin is not None and origin.rstrip("/") != settings.public_origin.rstrip("/")
            ):
                return JSONResponse(
                    status_code=403,
                    content={
                        "error": {
                            "code": "FORBIDDEN",
                            "message": "Origem de solicitação não autorizada.",
                        }
                    },
                )
        response = await call_next(request)
        response.headers.update(
            {
                "X-Request-ID": request_id,
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
                "Referrer-Policy": "same-origin",
            }
        )
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration_ms": round((time.monotonic() - started) * 1000, 2),
                }
            )
        )
        return response

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        return JSONResponse(
            status_code=exc.status, content={"error": {"code": exc.code, "message": exc.message}}
        )

    @app.exception_handler(LedgerError)
    async def ledger_error(request, exc):
        return JSONResponse(
            status_code=422, content={"error": {"code": "INVALID_EVENT", "message": str(exc)}}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        fields = ", ".join(".".join(str(x) for x in error["loc"][1:]) for error in exc.errors())
        return JSONResponse(
            status_code=422,
            content={
                "error": {"code": "VALIDATION_ERROR", "message": f"Confira os campos: {fields}."}
            },
        )

    @app.exception_handler(IntegrityError)
    async def conflict_error(request, exc):
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "CONFLICT",
                    "message": "Registro duplicado ou alteração incompatível. Atualize os dados.",
                }
            },
        )

    @app.exception_handler(OperationalError)
    async def storage_error(request, exc):
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "STORAGE_UNAVAILABLE",
                    "message": "Dados temporariamente indisponíveis. Tente novamente.",
                }
            },
        )

    @app.get("/api/v1/health")
    def health(db: DB):
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ready", "version": "0.1.0"}

    @app.get("/api/v1/openapi.json")
    def schema(actor: Actor):
        return app.openapi()

    @app.post("/api/v1/auth/login", response_model=AuthRead)
    def login(payload: Login, response: Response, db: DB):
        user, token = authenticate(db, str(payload.email), payload.password, settings.session_hours)
        response.set_cookie(
            "hub_session",
            token,
            max_age=settings.session_hours * 3600,
            secure=settings.cookie_secure,
            httponly=True,
            samesite="strict",
            path="/",
        )
        return {"user": public_user(user)}

    @app.get("/api/v1/auth/session", response_model=AuthRead)
    def session(actor: Actor):
        return {"user": public_user(actor)}

    @app.post("/api/v1/auth/logout", status_code=204)
    def logout(request: Request, response: Response, db: DB, actor: Actor):
        token = request.cookies.get("hub_session", "")
        db.execute(delete(AuthSession).where(AuthSession.token_hash == digest(token)))
        audit(db, actor, "logout", "user", actor.id)
        db.commit()
        response.delete_cookie(
            "hub_session", path="/", secure=settings.cookie_secure, httponly=True, samesite="strict"
        )

    @app.get("/api/v1/members", response_model=Page[UserRead])
    def members(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.scalars(
            select(User)
            .where(User.active.is_(True))
            .order_by(User.name, User.id)
            .limit(limit)
            .offset(offset)
        )
        return page(
            [public_user(u) for u in rows],
            db.scalar(select(func.count()).select_from(User).where(User.active.is_(True))),
            limit,
            offset,
        )

    @app.post("/api/v1/members", status_code=201, response_model=UserRead)
    def member_create(payload: MemberCreate, db: DB, actor: Actor):
        require_admin(actor)
        user = User(
            name=payload.name,
            email=str(payload.email),
            role=payload.role,
            password_hash=hasher.hash(payload.password),
        )
        db.add(user)
        db.flush()
        audit(db, actor, "create", "user", user.id)
        db.commit()
        return public_user(user)

    @app.get("/api/v1/owners", response_model=Page[OwnerRead])
    def owners(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.scalars(select(Owner).order_by(Owner.name, Owner.id).limit(limit).offset(offset))
        return page(
            [{"id": r.id, "name": r.name} for r in rows],
            db.scalar(select(func.count()).select_from(Owner)),
            limit,
            offset,
        )

    @app.post("/api/v1/owners", status_code=201, response_model=OwnerRead)
    def owner_create(payload: OwnerCreate, db: DB, actor: Actor):
        require_writer(actor)
        row = Owner(name=payload.name)
        db.add(row)
        db.flush()
        audit(db, actor, "create", "owner", row.id)
        db.commit()
        return {"id": row.id, "name": row.name}

    @app.get("/api/v1/portfolios", response_model=Page[PortfolioRead])
    def portfolios(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.scalars(
            select(Portfolio).order_by(Portfolio.name, Portfolio.id).limit(limit).offset(offset)
        )
        return page(
            [portfolio_item(db, r) for r in rows],
            db.scalar(select(func.count()).select_from(Portfolio)),
            limit,
            offset,
        )

    @app.post("/api/v1/portfolios", status_code=201, response_model=PortfolioRead)
    def portfolio_create(payload: PortfolioCreate, db: DB, actor: Actor):
        require_writer(actor)
        owner = need(db, Owner, payload.owner_id)
        account = Account(owner_id=owner.id, name=payload.account_name, currency=payload.currency)
        db.add(account)
        db.flush()
        row = Portfolio(
            owner_id=owner.id, account_id=account.id, name=payload.name, currency=payload.currency
        )
        db.add(row)
        db.flush()
        audit(db, actor, "create", "portfolio", row.id)
        db.commit()
        return portfolio_item(db, row)

    @app.get("/api/v1/instruments", response_model=Page[InstrumentRead])
    def instruments(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.execute(
            select(Instrument, Listing)
            .join(Listing)
            .order_by(Listing.ticker, Instrument.id)
            .limit(limit)
            .offset(offset)
        )
        return page(
            [
                {
                    "id": r.id,
                    "name": r.name,
                    "asset_class": r.asset_class,
                    "currency": r.currency,
                    "ticker": listing.ticker,
                    "exchange": listing.exchange,
                }
                for r, listing in rows
            ],
            db.scalar(select(func.count()).select_from(Instrument)),
            limit,
            offset,
        )

    @app.post("/api/v1/instruments", status_code=201, response_model=InstrumentRead)
    def instrument_create(payload: InstrumentCreate, db: DB, actor: Actor):
        require_writer(actor)
        issuer = None
        if payload.issuer_name:
            issuer = Issuer(name=payload.issuer_name)
            db.add(issuer)
            db.flush()
        row = Instrument(
            name=payload.name,
            asset_class=payload.asset_class,
            currency=payload.currency,
            issuer_id=issuer.id if issuer else None,
        )
        db.add(row)
        db.flush()
        listing = Listing(
            instrument_id=row.id, ticker=payload.ticker.upper(), exchange=payload.exchange.upper()
        )
        db.add(listing)
        audit(db, actor, "create", "instrument", row.id)
        db.commit()
        return {
            "id": row.id,
            "name": row.name,
            "asset_class": row.asset_class,
            "currency": row.currency,
            "ticker": listing.ticker,
            "exchange": listing.exchange,
        }

    @app.post("/api/v1/prices", status_code=201, response_model=PriceRead)
    def price_create(payload: PriceCreate, db: DB, actor: Actor):
        require_writer(actor)
        need(db, Instrument, payload.instrument_id)
        row = Price(
            instrument_id=str(payload.instrument_id),
            price=payload.price,
            as_of=payload.as_of,
            source=payload.source,
            created_by=actor.id,
            raw_payload_hash=digest(payload.model_dump_json()),
        )
        db.add(row)
        db.flush()
        audit(db, actor, "record", "price", row.id)
        db.commit()
        return {
            "id": row.id,
            "instrument_id": row.instrument_id,
            "price": decimal_string(row.price),
            "as_of": row.as_of.isoformat(),
            "source": row.source,
            "retrieved_at": row.retrieved_at.isoformat(),
        }

    @app.get("/api/v1/transactions", response_model=Page[TransactionRead])
    def transactions(
        db: DB,
        actor: Actor,
        portfolio_id: UUID | None = None,
        owner_id: UUID | None = None,
        as_of: date | None = None,
        limit: Limit = 100,
        offset: Offset = 0,
    ):
        query = select(Transaction).where(Transaction.trade_date <= (as_of or today()))
        if portfolio_id:
            query = query.where(Transaction.portfolio_id == str(portfolio_id))
        if owner_id:
            query = query.where(Transaction.owner_id == str(owner_id))
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        rows = db.scalars(
            query.order_by(Transaction.trade_date.desc(), Transaction.sequence.desc())
            .limit(limit)
            .offset(offset)
        )
        return page([transaction_item(db, row) for row in rows], total, limit, offset)

    @app.post("/api/v1/transactions", status_code=201, response_model=TransactionRead)
    def transaction_create(payload: TransactionCreate, db: DB, actor: Actor, response: Response):
        require_writer(actor)
        # Serialize writes to each portfolio BEFORE reading ledger/idempotency state.
        portfolio = db.scalar(
            select(Portfolio).where(Portfolio.id == str(payload.portfolio_id)).with_for_update()
        )
        if not portfolio:
            raise AppError(404, "NOT_FOUND", "Carteira não encontrada.")
        request_hash = canonical_hash(payload)
        duplicate = db.scalar(
            select(Transaction).where(
                Transaction.portfolio_id == portfolio.id,
                Transaction.idempotency_key == payload.idempotency_key,
            )
        )
        if not duplicate and payload.external_id:
            duplicate = db.scalar(
                select(Transaction).where(
                    Transaction.portfolio_id == portfolio.id,
                    Transaction.source == payload.source,
                    Transaction.external_id == payload.external_id,
                )
            )
        if duplicate:
            if duplicate.payload_hash != request_hash:
                raise AppError(
                    409, "CONFLICT", "A mesma identificação já foi usada com outros dados."
                )
            response.status_code = 200
            return transaction_item(db, duplicate)
        if payload.instrument_id:
            need(db, Instrument, payload.instrument_id)
        rows = event_rows(db, [portfolio.id], today(), for_append=True)
        if rows and payload.trade_date < rows[-1].trade_date:
            raise AppError(
                409,
                "CHRONOLOGY_CONFLICT",
                "Registre os eventos em ordem cronológica. Retificação histórica ainda pendente.",
            )
        state = replay(rows)
        event = Event(
            payload.event_type,
            payload.trade_date,
            str(payload.instrument_id) if payload.instrument_id else None,
            payload.quantity,
            payload.unit_price,
            payload.gross_amount,
            payload.fees,
            payload.taxes,
        )
        postings = apply_event(state, event)
        gross = event_gross(event)
        row = Transaction(
            portfolio_id=portfolio.id,
            owner_id=portfolio.owner_id,
            broker_account_id=portfolio.account_id,
            instrument_id=event.instrument_id,
            event_type=payload.event_type,
            quantity=payload.quantity,
            unit_price=payload.unit_price,
            gross_amount=gross,
            fees=payload.fees,
            taxes=payload.taxes,
            trade_date=payload.trade_date,
            settlement_date=payload.settlement_date,
            source=payload.source,
            external_id=payload.external_id,
            idempotency_key=payload.idempotency_key,
            payload_hash=request_hash,
            notes=payload.notes,
            created_by=actor.id,
        )
        db.add(row)
        db.flush()
        db.add_all(
            [
                JournalEntry(
                    transaction_id=row.id,
                    account=p.account,
                    amount=p.amount,
                    instrument_id=p.instrument_id,
                    quantity=p.quantity,
                )
                for p in postings
            ]
        )
        audit(db, actor, "record", "transaction", row.id)
        db.commit()
        return transaction_item(db, row)

    def consistent_dashboard(as_of, portfolio_id, owner_id):
        cutoff = as_of or today()
        if cutoff > today():
            raise AppError(422, "INVALID_DATE", "Data de análise não pode ser futura.")
        with Session(engine.execution_options(isolation_level="REPEATABLE READ")) as snapshot:
            return dashboard(
                snapshot,
                cutoff,
                str(portfolio_id) if portfolio_id else None,
                str(owner_id) if owner_id else None,
            )

    @app.get("/api/v1/dashboard", response_model=DashboardRead)
    def dashboard_get(
        actor: Actor,
        as_of: date | None = None,
        portfolio_id: UUID | None = None,
        owner_id: UUID | None = None,
    ):
        return consistent_dashboard(as_of, portfolio_id, owner_id)

    @app.get("/api/v1/reports/positions.csv")
    def export(
        actor: Actor,
        as_of: date | None = None,
        portfolio_id: UUID | None = None,
        owner_id: UUID | None = None,
        snapshot_id: str | None = None,
    ):
        result = consistent_dashboard(as_of, portfolio_id, owner_id)
        if snapshot_id and snapshot_id != result["snapshot_id"]:
            raise AppError(
                409, "SNAPSHOT_CHANGED", "Os dados mudaram. Atualize o painel antes de exportar."
            )
        content = io.StringIO(newline="")
        writer = csv.writer(content)
        writer.writerow(
            [
                "data",
                "carteira",
                "titular",
                "ativo",
                "quantidade",
                "custo_brl",
                "valor_mercado_brl",
                "data_avaliacao",
                "fonte",
                "qualidade",
                "snapshot",
                "metodo",
            ]
        )

        def safe(value):
            value = "" if value is None else str(value)
            return (
                "'" + value
                if value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r"))
                else value
            )

        for position in result["positions"]:
            writer.writerow(
                [
                    safe(v)
                    for v in [
                        result["as_of"],
                        position["portfolio_name"],
                        position["owner_name"],
                        position["ticker"],
                        position["quantity"],
                        position["cost_basis"],
                        position["market_value"],
                        position["price_as_of"],
                        position["price_source"],
                        position["quality"],
                        result["snapshot_id"],
                        result["method_version"],
                    ]
                ]
            )
        return Response(
            "\ufeff" + content.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="posicoes.csv"'},
        )

    @app.get("/api/v1/audit", response_model=Page[AuditRead])
    def audit_get(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.execute(
            select(AuditEvent, User.name)
            .join(User, User.id == AuditEvent.actor_id)
            .order_by(AuditEvent.id.desc())
            .limit(limit)
            .offset(offset)
        )
        return page(
            [
                {
                    "id": str(row.id),
                    "action": row.action,
                    "entity_type": row.entity_type,
                    "entity_id": row.entity_id,
                    "actor_name": name,
                    "created_at": row.created_at.isoformat(),
                }
                for row, name in rows
            ],
            db.scalar(select(func.count()).select_from(AuditEvent)),
            limit,
            offset,
        )

    return app


app = create_app()
