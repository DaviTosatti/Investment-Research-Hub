from typing import Literal

from pydantic import BaseModel, Field

from hub_api.import_schemas import PreviewCreate, RowDecision
from hub_api.responses import Page

RowStatus = Literal["ready", "duplicate", "needs_review", "quarantined", "excluded"]


class SourceRead(BaseModel):
    id: str
    name: str
    kind: Literal["statement_upload"]
    created_by: str
    created_at: str
    coverage: str


class ImportSummary(BaseModel):
    ready: int
    duplicate: int
    needs_review: int
    quarantined: int
    excluded: int
    can_commit: bool
    cash_before: str
    cash_after: str
    currency: Literal["BRL"]
    quantity_unit: str
    amount_unit: str
    period_start: str | None
    period_end: str | None
    method_version: str


class ImportRowRead(BaseModel):
    row_number: int
    raw: dict[str, str | None]
    normalized: dict[str, str | None] | None
    status: RowStatus
    errors: list[str]
    candidates: list[dict[str, str | int | None]]
    candidate_count: int = 0
    calculated_gross_amount: str | None = None
    decision: RowDecision | None
    transaction_id: str | None
    duplicate_of_row: int | None


class SnapshotRead(BaseModel):
    id: str
    revision: int
    summary: ImportSummary
    created_by: str
    created_at: str


class PreviewRead(SnapshotRead):
    import_id: str
    ledger_version: str
    config: PreviewCreate
    rows: list[ImportRowRead]


class ReceiptRowRead(BaseModel):
    row_number: int
    status: RowStatus
    transaction_id: str | None


class ReceiptRead(BaseModel):
    id: str
    import_id: str
    preview_id: str
    results: list[ReceiptRowRead]
    created_by: str
    created_at: str


class ImportBatchRead(BaseModel):
    id: str
    portfolio_id: str
    owner_id: str
    source_id: str
    source_name: str
    filename: str
    sha256: str
    size: int
    created_by: str
    created_at: str
    status: Literal["committed", "previewed", "uploaded"]
    summary: ImportSummary | None
    latest_preview_id: str | None
    original_url: str


class ImportSampleRead(BaseModel):
    number: int
    values: dict[str, str | None]
    errors: list[str]
    numeric_columns: list[str] = Field(default_factory=list)


class ImportDetailRead(ImportBatchRead):
    headers: list[str]
    sample: list[ImportSampleRead]
    row_count: int
    parse_options: dict[str, str | None]
    preview: PreviewRead | None
    receipt: ReceiptRead | None


class QualityRead(Page[ImportBatchRead]):
    scope: Literal["statement_imports"]
    coverage: str


class LineageRead(BaseModel):
    import_: ImportBatchRead = Field(alias="import")
    receipt: ReceiptRead | None
    snapshots_url: str
    source: SourceRead
    owner_id: str
