import type { EventType } from "./types";

export const importFields = [
  "event_type", "trade_date", "settlement_date", "ticker", "exchange", "instrument_id",
  "quantity", "unit_price", "gross_amount", "fees", "taxes", "external_id", "notes", "currency",
] as const;
export type ImportField = typeof importFields[number];
export type ImportStatus = "ready" | "duplicate" | "needs_review" | "quarantined" | "excluded";
export type RowEdit = { row_number: number; values: Partial<Record<ImportField, string | null>>; reason: string };
export type RowDecision = { row_number: number; action: "skip" | "create"; reason: string };
export type ImportConfig = {
  mapping: Partial<Record<ImportField, string>>;
  decimal_separator: "." | ",";
  date_format: "YYYY-MM-DD" | "DD/MM/YYYY";
  exchange: string;
  event_values: Record<string, EventType>;
  edits: RowEdit[];
  decisions: RowDecision[];
};
export type ParseOptions = { delimiter: ";" | "," | "\t"; encoding: "utf-8-sig" | "cp1252"; sheet: string | null };
export type ImportSource = { id: string; name: string; kind: string; coverage: string; created_by: string; created_at: string };
export type ImportSummary = Record<ImportStatus, number> & {
  can_commit: boolean; cash_before: string; cash_after: string; currency: string;
  quantity_unit: string; amount_unit: string; period_start: string | null; period_end: string | null; method_version: string;
};
export type ImportRow = {
  row_number: number; raw: Record<string, string | null>;
  normalized: Record<string, string | null> | null;
  status: ImportStatus; errors: string[];
  candidates: { transaction_id: string | null; row_number: number | null }[];
  candidate_count: number; calculated_gross_amount: string | null;
  decision: RowDecision | null; transaction_id: string | null; duplicate_of_row: number | null;
};
export type ImportPreview = {
  id: string; import_id: string; revision: number; ledger_version: string; config: ImportConfig;
  rows: ImportRow[]; summary: ImportSummary; created_by: string; created_at: string;
};
export type ImportReceipt = {
  id: string; import_id: string; preview_id: string; created_by: string; created_at: string;
  results: { row_number: number; status: ImportStatus; transaction_id: string | null }[];
};
export type ImportBatch = {
  id: string; portfolio_id: string; owner_id: string; source_id: string; source_name: string;
  filename: string; sha256: string; size: number; created_by: string; created_at: string;
  status: "uploaded" | "previewed" | "committed"; summary: ImportSummary | null;
  latest_preview_id: string | null; original_url: string;
};
export type ImportDetail = ImportBatch & {
  headers: string[];
  sample: { number: number; values: Record<string, string | null>; errors: string[]; numeric_columns?: string[] }[];
  row_count: number; parse_options: ParseOptions; preview: ImportPreview | null; receipt: ImportReceipt | null;
};
export type ImportSnapshot = Pick<ImportPreview, "id" | "revision" | "summary" | "created_by" | "created_at">;
