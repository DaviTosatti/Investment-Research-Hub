import { importFields, type ImportConfig, type ImportDetail, type ImportPreview, type ParseOptions, type RowDecision, type RowEdit } from "./import-types";

export const importPageSize = 25;
export const maxImportBytes = 2 * 1024 * 1024;

export function importCsvTemplate(delimiter: ParseOptions["delimiter"] = ";"): string {
  return `\uFEFF${importFields.join(delimiter)}\r\n`;
}

// Only canonical, exact column names are suggested. The user must review them.
export function initialImportConfig(headers: string[]): ImportConfig {
  return {
    mapping: Object.fromEntries(importFields.filter(field => headers.includes(field)).map(field => [field, field])),
    decimal_separator: ".", date_format: "YYYY-MM-DD", exchange: "B3", event_values: {}, edits: [], decisions: [],
  };
}

function stable(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === "object") return Object.fromEntries(Object.entries(value).sort(([a], [b]) => a.localeCompare(b)).map(([key, child]) => [key, stable(child)]));
  return value;
}

export function importConfigSignature(config: ImportConfig): string {
  return JSON.stringify(stable({
    ...config, event_values: config.event_values ?? {},
    edits: [...config.edits].sort((a, b) => a.row_number - b.row_number),
    decisions: [...config.decisions].sort((a, b) => a.row_number - b.row_number),
  }));
}

export type ConfigIssue = "required_mapping" | "missing_column" | "repeated_column" | "reason" | "exchange" | "row" | "edit_value" | "event_values";
export function importConfigIssue(config: ImportConfig, headers: string[]): ConfigIssue | null {
  if (!config.mapping.event_type || !config.mapping.trade_date) return "required_mapping";
  const columns = Object.values(config.mapping);
  if (columns.some(column => !headers.includes(column))) return "missing_column";
  if (new Set(columns).size !== columns.length) return "repeated_column";
  if (!config.exchange.trim() || config.exchange.length > 24) return "exchange";
  if (Object.keys(config.event_values ?? {}).length > 40) return "event_values";
  for (const rows of [config.edits, config.decisions]) {
    if (rows.length > 500 || new Set(rows.map(row => row.row_number)).size !== rows.length || rows.some(row => !Number.isInteger(row.row_number) || row.row_number < 2)) return "row";
    if (rows.some(row => row.reason.trim().length < 5 || row.reason.length > 500)) return "reason";
  }
  if (config.edits.some(edit => Object.values(edit.values).some(value => value !== null && value !== undefined && value.length > 2000))) return "edit_value";
  return null;
}

export function updateRowEdit(config: ImportConfig, edit: RowEdit | null, rowNumber: number): ImportConfig {
  return { ...config, edits: [...config.edits.filter(row => row.row_number !== rowNumber), ...(edit ? [edit] : [])] };
}
export function updateRowDecision(config: ImportConfig, decision: RowDecision | null, rowNumber: number): ImportConfig {
  return { ...config, decisions: [...config.decisions.filter(row => row.row_number !== rowNumber), ...(decision ? [decision] : [])] };
}

export function canConfirmImport(input: {
  importId: string; latestPreviewId: string | null; preview: ImportPreview | null;
  config: ImportConfig; canWrite: boolean; pending: boolean; historical: boolean;
  stale: boolean; committed: boolean; acknowledged: boolean;
}): boolean {
  const { preview } = input;
  return input.canWrite && !input.pending && !input.historical && !input.stale && !input.committed && input.acknowledged
    && !!preview && preview.import_id === input.importId && preview.id === input.latestPreviewId
    && preview.summary.can_commit && !preview.rows.some(row => row.status === "needs_review" || row.status === "quarantined")
    && importConfigSignature(preview.config) === importConfigSignature(input.config);
}

export function importFileIssue(file: Pick<File, "name" | "size">): "type" | "size" | "empty" | "name" | null {
  if (!/\.(csv|xlsx)$/i.test(file.name)) return "type";
  if (!file.size) return "empty";
  if (file.size > maxImportBytes) return "size";
  if (file.name.length > 180 || /[\\/\x00-\x1f\x7f]/.test(file.name)) return "name";
  return null;
}

export function importUploadPath(portfolioId: string, sourceId: string, filename: string, options: ParseOptions): string {
  const query = new URLSearchParams({ portfolio_id: portfolioId, source_id: sourceId, filename, delimiter: options.delimiter, encoding: options.encoding });
  if (options.sheet?.trim()) query.set("sheet", options.sheet.trim());
  return `/imports?${query}`;
}

// Never turn a server-provided original URL into a public/external download.
export function privateOriginalUrl(batch: Pick<ImportDetail, "id" | "original_url">): string | null {
  const expected = `/api/v1/imports/${encodeURIComponent(batch.id)}/original`;
  return batch.original_url === expected ? expected : null;
}

export type ImportSelection = { portfolioId: string; importId: string };
export function readImportSelection(storage: Pick<Storage, "getItem">, userId: string): ImportSelection {
  try {
    const value: unknown = JSON.parse(storage.getItem(`hub:imports:${userId}`) ?? "null");
    if (value && typeof value === "object" && "portfolioId" in value && "importId" in value && typeof value.portfolioId === "string" && typeof value.importId === "string") return { portfolioId: value.portfolioId, importId: value.importId };
  } catch { /* Storage may be disabled; server history remains available. */ }
  return { portfolioId: "", importId: "" };
}
export function saveImportSelection(storage: Pick<Storage, "setItem">, userId: string, selection: ImportSelection): void {
  try { storage.setItem(`hub:imports:${userId}`, JSON.stringify(selection)); } catch { /* Selection persistence is optional. */ }
}
