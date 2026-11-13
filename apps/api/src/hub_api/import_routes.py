from typing import Annotated, Literal
from urllib.parse import quote
from uuid import UUID

from fastapi import Depends, FastAPI, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session, defer
from starlette.concurrency import run_in_threadpool

from hub_api.errors import AppError
from hub_api.import_responses import (
    ImportBatchRead,
    ImportDetailRead,
    LineageRead,
    PreviewRead,
    QualityRead,
    ReceiptRead,
    SnapshotRead,
    SourceRead,
)
from hub_api.import_schemas import ImportConfirm, PreviewCreate, SourceCreate
from hub_api.import_service import (
    audit_import,
    build_preview,
    confirm,
    get_batch,
    latest_preview,
    upload,
)
from hub_api.models import (
    DataSource,
    ImportBatch,
    ImportPreview,
    ImportReceipt,
    OriginalFile,
    Portfolio,
    User,
)
from hub_api.responses import Page
from hub_api.security import require_writer


def source_item(source: DataSource) -> dict:
    return {
        "id": source.id,
        "name": source.name,
        "kind": source.kind,
        "created_by": source.created_by,
        "created_at": source.created_at.isoformat(),
        "coverage": "Operações realizadas em BRL, enviadas pelo usuário. Sem coleta externa automática.",
    }


def preview_item(preview: ImportPreview | None) -> dict | None:
    if preview is None:
        return None
    return {
        "id": preview.id,
        "import_id": preview.import_id,
        "revision": preview.revision,
        "ledger_version": preview.ledger_version,
        "config": preview.config,
        "rows": preview.rows,
        "summary": preview.summary,
        "created_by": preview.created_by,
        "created_at": preview.created_at.isoformat(),
    }


def receipt_item(receipt: ImportReceipt | None) -> dict | None:
    if receipt is None:
        return None
    return {
        "id": receipt.id,
        "import_id": receipt.import_id,
        "preview_id": receipt.preview_id,
        "results": receipt.results,
        "created_by": receipt.created_by,
        "created_at": receipt.created_at.isoformat(),
    }


def batch_item(db: Session, batch: ImportBatch, *, detail: bool = False) -> dict:
    original = db.scalar(
        select(OriginalFile)
        .options(defer(OriginalFile.content))
        .where(OriginalFile.id == batch.original_id)
    )
    receipt_query = select(ImportReceipt).where(ImportReceipt.import_id == batch.id)
    if not detail:
        receipt_query = receipt_query.options(defer(ImportReceipt.results))
    receipt = db.scalar(receipt_query)
    # A concurrent confirmation must never pair a receipt with another revision.
    preview = (
        db.get(
            ImportPreview,
            receipt.preview_id,
            options=(() if detail else (defer(ImportPreview.rows), defer(ImportPreview.config))),
        )
        if receipt
        else latest_preview(db, batch.id, summary_only=not detail)
    )
    portfolio = db.get(Portfolio, batch.portfolio_id)
    result = {
        "id": batch.id,
        "portfolio_id": batch.portfolio_id,
        "owner_id": portfolio.owner_id,
        "source_id": batch.source_id,
        "source_name": db.get(DataSource, batch.source_id).name,
        "filename": batch.filename,
        "sha256": original.sha256,
        "size": original.size,
        "created_by": batch.created_by,
        "created_at": batch.created_at.isoformat(),
        "status": "committed" if receipt else "previewed" if preview else "uploaded",
        "summary": preview.summary if preview else None,
        "latest_preview_id": preview.id if preview else None,
        "original_url": f"/api/v1/imports/{batch.id}/original",
    }
    if detail:
        result.update(
            headers=batch.table["headers"],
            sample=batch.table["rows"][:10],
            row_count=len(batch.table["rows"]),
            parse_options=batch.parse_options,
            preview=preview_item(preview),
            receipt=receipt_item(receipt),
        )
    return result


def register_import_routes(app: FastAPI, get_db, get_user) -> None:
    DB = Annotated[Session, Depends(get_db)]
    Actor = Annotated[User, Depends(get_user)]
    Limit = Annotated[int, Query(ge=1, le=200)]
    Offset = Annotated[int, Query(ge=0)]

    @app.get("/api/v1/sources", response_model=Page[SourceRead], tags=["Ingestão e qualidade"])
    def sources(db: DB, actor: Actor, limit: Limit = 100, offset: Offset = 0):
        rows = db.scalars(
            select(DataSource).order_by(DataSource.name_key).limit(limit).offset(offset)
        )
        return {
            "items": [source_item(r) for r in rows],
            "total": db.scalar(select(func.count()).select_from(DataSource)),
            "limit": limit,
            "offset": offset,
        }

    @app.post(
        "/api/v1/sources", response_model=SourceRead, status_code=201, tags=["Ingestão e qualidade"]
    )
    def create_source(payload: SourceCreate, db: DB, actor: Actor):
        require_writer(actor)
        row = DataSource(name=payload.name, name_key=payload.name.casefold(), created_by=actor.id)
        db.add(row)
        db.flush()
        audit_import(db, actor, "create", "source", row.id)
        db.commit()
        return source_item(row)

    @app.get("/api/v1/imports", response_model=Page[ImportBatchRead], tags=["Ingestão e qualidade"])
    def imports(
        db: DB,
        actor: Actor,
        portfolio_id: UUID | None = None,
        limit: Limit = 100,
        offset: Offset = 0,
    ):
        query = select(ImportBatch).options(defer(ImportBatch.table))
        if portfolio_id:
            query = query.where(ImportBatch.portfolio_id == str(portfolio_id))
        total = db.scalar(select(func.count()).select_from(query.subquery()))
        rows = db.scalars(
            query.order_by(ImportBatch.created_at.desc(), ImportBatch.id)
            .limit(limit)
            .offset(offset)
        )
        return {
            "items": [batch_item(db, r) for r in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    @app.post(
        "/api/v1/imports",
        response_model=ImportDetailRead,
        status_code=201,
        tags=["Ingestão e qualidade"],
        openapi_extra={
            "requestBody": {
                "required": True,
                "content": {
                    "application/octet-stream": {"schema": {"type": "string", "format": "binary"}}
                },
            }
        },
    )
    async def upload_import(
        request: Request,
        response: Response,
        db: DB,
        actor: Actor,
        portfolio_id: UUID,
        source_id: UUID,
        filename: Annotated[str, Query(min_length=1, max_length=180)],
        delimiter: Literal[";", ",", "\t"] = ";",
        encoding: Literal["utf-8-sig", "cp1252"] = "utf-8-sig",
        sheet: Annotated[str | None, Query(max_length=100)] = None,
    ):
        require_writer(actor)
        content = bytearray()
        async for chunk in request.stream():
            if len(content) + len(chunk) > 2 * 1024 * 1024:
                raise AppError(413, "FILE_TOO_LARGE", "O arquivo excede o limite de 2 MiB.")
            content.extend(chunk)

        def save():
            batch, created = upload(
                db,
                actor,
                str(portfolio_id),
                str(source_id),
                filename,
                bytes(content),
                {"delimiter": delimiter, "encoding": encoding, "sheet": sheet},
            )
            db.commit()
            return batch_item(db, batch, detail=True), created

        result, created = await run_in_threadpool(save)
        if not created:
            response.status_code = 200
        return result

    @app.get(
        "/api/v1/imports/{import_id}",
        response_model=ImportDetailRead,
        tags=["Ingestão e qualidade"],
    )
    def import_detail(import_id: UUID, db: DB, actor: Actor):
        return batch_item(db, get_batch(db, str(import_id)), detail=True)

    @app.get("/api/v1/imports/{import_id}/original", tags=["Ingestão e qualidade"])
    def original(import_id: UUID, db: DB, actor: Actor):
        batch = get_batch(db, str(import_id))
        content = db.get(OriginalFile, batch.original_id)
        return Response(
            content.content,
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{quote(batch.filename, safe='')}",
                "X-Content-SHA256": content.sha256,
            },
        )

    @app.post(
        "/api/v1/imports/{import_id}/preview",
        response_model=PreviewRead,
        status_code=201,
        tags=["Ingestão e qualidade"],
    )
    def preview(import_id: UUID, payload: PreviewCreate, db: DB, actor: Actor):
        require_writer(actor)
        row = build_preview(db, get_batch(db, str(import_id), lock=True), payload, actor)
        db.commit()
        return preview_item(row)

    @app.post(
        "/api/v1/imports/{import_id}/confirm",
        response_model=ReceiptRead,
        status_code=201,
        tags=["Ingestão e qualidade"],
    )
    def confirm_import(
        import_id: UUID, payload: ImportConfirm, db: DB, actor: Actor, response: Response
    ):
        require_writer(actor)
        row, created = confirm(
            db, get_batch(db, str(import_id), lock=True), str(payload.preview_id), actor
        )
        db.commit()
        if not created:
            response.status_code = 200
        return receipt_item(row)

    @app.get("/api/v1/snapshots", response_model=Page[SnapshotRead], tags=["Ingestão e qualidade"])
    def snapshots(db: DB, actor: Actor, import_id: UUID, limit: Limit = 100, offset: Offset = 0):
        get_batch(db, str(import_id))
        query = select(ImportPreview).options(
            defer(ImportPreview.rows), defer(ImportPreview.config)
        )
        query = query.where(ImportPreview.import_id == str(import_id))
        rows = db.scalars(query.order_by(ImportPreview.revision.desc()).limit(limit).offset(offset))
        return {
            "items": [
                {
                    "id": r.id,
                    "revision": r.revision,
                    "summary": r.summary,
                    "created_by": r.created_by,
                    "created_at": r.created_at.isoformat(),
                }
                for r in rows
            ],
            "total": db.scalar(select(func.count()).select_from(query.subquery())),
            "limit": limit,
            "offset": offset,
        }

    @app.get(
        "/api/v1/snapshots/{snapshot_id}", response_model=PreviewRead, tags=["Ingestão e qualidade"]
    )
    def snapshot(snapshot_id: UUID, db: DB, actor: Actor):
        row = db.get(ImportPreview, str(snapshot_id))
        if row is None:
            raise AppError(404, "NOT_FOUND", "Snapshot de importação não encontrado.")
        return preview_item(row)

    @app.get("/api/v1/quality", response_model=QualityRead, tags=["Ingestão e qualidade"])
    def quality(
        db: DB,
        actor: Actor,
        portfolio_id: UUID | None = None,
        limit: Limit = 100,
        offset: Offset = 0,
    ):
        result = imports(db, actor, portfolio_id, limit, offset)
        return {
            **result,
            "scope": "statement_imports",
            "coverage": "Qualidade dos arquivos enviados; não certifica a cobertura de provedores externos.",
        }

    @app.get("/api/v1/lineage", response_model=LineageRead, tags=["Ingestão e qualidade"])
    def lineage(db: DB, actor: Actor, import_id: UUID):
        batch = get_batch(db, str(import_id))
        detail = batch_item(db, batch, detail=True)
        return {
            "import": detail,
            "receipt": detail["receipt"],
            "snapshots_url": f"/api/v1/snapshots?import_id={batch.id}",
            "source": source_item(db.get(DataSource, batch.source_id)),
            "owner_id": db.get(Portfolio, batch.portfolio_id).owner_id,
        }
