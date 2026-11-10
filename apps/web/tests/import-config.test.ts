import assert from "node:assert/strict";
import test from "node:test";
import {
  canConfirmImport, importConfigIssue, importConfigSignature, importCsvTemplate, importFileIssue,
  importUploadPath, initialImportConfig, maxImportBytes, privateOriginalUrl, readImportSelection,
  saveImportSelection, updateRowDecision, updateRowEdit,
} from "../src/lib/import-config";
import { importFields, type ImportConfig, type ImportPreview } from "../src/lib/import-types";

const headers = ["event_type", "trade_date", "gross_amount"];
const config = (): ImportConfig => initialImportConfig(headers);
const preview = (): ImportPreview => ({
  id: "preview-2", import_id: "import-1", revision: 2, ledger_version: "ledger-version",
  config: config(), rows: [{ row_number: 2, raw: { event_type: "aporte", trade_date: "2026-11-01", gross_amount: "123456789.12345678" }, normalized: { event_type: "deposit", trade_date: "2026-11-01", gross_amount: "123456789.12345678" }, status: "ready", errors: [], candidates: [], candidate_count: 0, calculated_gross_amount: "123456789.12345678", decision: null, transaction_id: null, duplicate_of_row: null }],
  summary: { ready: 1, duplicate: 0, needs_review: 0, quarantined: 0, excluded: 0, can_commit: true, cash_before: "0", cash_after: "123456789.12345678", currency: "BRL", amount_unit: "BRL", quantity_unit: "units_or_split_factor", period_start: "2026-11-01", period_end: "2026-11-01", method_version: "method" },
  created_at: "2026-11-01T12:00:00Z", created_by: "member-1",
});
const confirmInput = () => ({ importId: "import-1", latestPreviewId: "preview-2", preview: preview(), config: config(), canWrite: true, pending: false, historical: false, stale: false, committed: false, acknowledged: true });

test("column suggestions require exact canonical spelling, with no guesses or fabricated values", () => {
  assert.deepEqual(initialImportConfig(["Event_Type", " trade_date ", "Amount", "quantity"]).mapping, { quantity: "quantity" });
  assert.deepEqual(config().mapping, { event_type: "event_type", trade_date: "trade_date", gross_amount: "gross_amount" });
  assert.equal(config().mapping.fees, undefined);
  assert.equal(config().mapping.settlement_date, undefined);
});

test("CSV templates contain every supported canonical header and no data rows", () => {
  for (const delimiter of [";", ",", "\t"] as const) {
    const template = importCsvTemplate(delimiter);
    assert.equal(template, `\uFEFF${importFields.join(delimiter)}\r\n`);
    assert.equal(template.trim().split(/\r?\n/).length, 1);
  }
});

test("mapping requires event/date and rejects absent or reused columns", () => {
  assert.equal(importConfigIssue(initialImportConfig(["gross_amount"]), headers), "required_mapping");
  assert.equal(importConfigIssue({ ...config(), mapping: { event_type: "event_type", trade_date: "event_type" } }, headers), "repeated_column");
  assert.equal(importConfigIssue({ ...config(), mapping: { ...config().mapping, fees: "missing" } }, headers), "missing_column");
  assert.equal(importConfigIssue(config(), headers), null);
});

test("row corrections preserve precise strings and explicit nulls without changing the original config", () => {
  const original = config();
  const corrected = updateRowEdit(original, { row_number: 2, values: { gross_amount: "123456789012345.12345678", settlement_date: null }, reason: "Conferido no extrato original" }, 2);
  assert.deepEqual(original.edits, []);
  assert.equal(corrected.edits[0].values.gross_amount, "123456789012345.12345678");
  assert.equal(corrected.edits[0].values.settlement_date, null);
  const replaced = updateRowEdit(corrected, { ...corrected.edits[0], values: { gross_amount: "1,25" } }, 2);
  assert.equal(replaced.edits.length, 1);
  assert.equal(updateRowEdit(replaced, null, 2).edits.length, 0);
});

test("every manual correction and decision requires a meaningful reason, including excluded rows", () => {
  for (const reason of ["", "1234", "     ", "    ok    ", "a".repeat(501)]) {
    assert.equal(importConfigIssue(updateRowDecision(config(), { row_number: 2, action: "skip", reason }, 2), headers), "reason");
    assert.equal(importConfigIssue(updateRowEdit(config(), { row_number: 2, values: { quantity: "1" }, reason }, 2), headers), "reason");
  }
  const decision = { row_number: 2, action: "create" as const, reason: "Execução distinta conferida" };
  assert.equal(importConfigIssue(updateRowDecision(config(), decision, 2), headers), null);
  const replaced = updateRowDecision(updateRowDecision(config(), decision, 2), { ...decision, action: "skip" }, 2);
  assert.equal(replaced.decisions.length, 1);
  assert.equal(replaced.decisions[0].action, "skip");
});

test("signatures ignore serialization order but retain exact values, nulls, reasons and actions", () => {
  const a = updateRowEdit(config(), { row_number: 3, values: { fees: "0", taxes: null }, reason: "Motivo conferido" }, 3);
  const b = { ...a, mapping: { gross_amount: "gross_amount", trade_date: "trade_date", event_type: "event_type" }, edits: [{ ...a.edits[0], values: { taxes: null, fees: "0" } }] };
  assert.equal(importConfigSignature(a), importConfigSignature(b));
  assert.notEqual(importConfigSignature(a), importConfigSignature({ ...a, edits: [{ ...a.edits[0], values: { fees: "0", taxes: "0" } }] }));
});

test("confirmation requires the reviewed current preview, active import, writer and acknowledgement", () => {
  assert.equal(canConfirmImport(confirmInput()), true);
  const blocked = [
    { canWrite: false }, { pending: true }, { historical: true }, { stale: true }, { committed: true },
    { acknowledged: false }, { importId: "other-import" }, { latestPreviewId: "newer-preview" }, { preview: null },
  ];
  for (const override of blocked) assert.equal(canConfirmImport({ ...confirmInput(), ...override }), false, JSON.stringify(override));
});

test("every changed config facet blocks confirmation of the previously reviewed ID", () => {
  const changes: ImportConfig[] = [
    { ...config(), mapping: { ...config().mapping, gross_amount: "other-column" } },
    { ...config(), decimal_separator: "," }, { ...config(), date_format: "DD/MM/YYYY" },
    { ...config(), exchange: "OTHER" }, { ...config(), event_values: { cash: "deposit" } },
    updateRowEdit(config(), { row_number: 2, values: { gross_amount: "2.00" }, reason: "Corrigido no original" }, 2),
    updateRowDecision(config(), { row_number: 2, action: "skip", reason: "Linha excluída manualmente" }, 2),
    updateRowDecision(config(), { row_number: 2, action: "create", reason: "Fato econômico distinto" }, 2),
  ];
  for (const next of changes) assert.equal(canConfirmImport({ ...confirmInput(), config: next }), false);
});

test("quarantine and ambiguous matches cannot be confirmed, even if a stale summary claims otherwise", () => {
  for (const status of ["needs_review", "quarantined"] as const) {
    const current = preview(); current.rows[0].status = status;
    assert.equal(canConfirmImport({ ...confirmInput(), preview: current }), false);
  }
  const current = preview(); current.summary.can_commit = false;
  assert.equal(canConfirmImport({ ...confirmInput(), preview: current }), false);
});

test("upload validation enforces nonempty CSV/XLSX, 2 MiB and safe filename bounds", () => {
  assert.equal(importFileIssue({ name: "Extrato.xlsx", size: maxImportBytes }), null);
  assert.equal(importFileIssue({ name: "extrato.CSV", size: 1 }), null);
  assert.equal(importFileIssue({ name: "extrato.csv", size: maxImportBytes + 1 }), "size");
  assert.equal(importFileIssue({ name: "extrato.csv", size: 0 }), "empty");
  assert.equal(importFileIssue({ name: "extrato.xls", size: 1 }), "type");
  assert.equal(importFileIssue({ name: "../extrato.csv", size: 1 }), "name");
  assert.equal(importFileIssue({ name: `${"a".repeat(181)}.csv`, size: 1 }), "name");
});

test("upload query encodes file/sheet names, tab delimiter and source/portfolio without changing them", () => {
  const path = importUploadPath("portfolio-id", "source-id", "Extrato & ações.csv", { delimiter: "\t", encoding: "cp1252", sheet: "Operações & taxas" });
  const url = new URL(path, "http://localhost");
  assert.equal(url.pathname, "/imports");
  assert.deepEqual(Object.fromEntries(url.searchParams), { portfolio_id: "portfolio-id", source_id: "source-id", filename: "Extrato & ações.csv", delimiter: "\t", encoding: "cp1252", sheet: "Operações & taxas" });
  assert.equal(new URL(importUploadPath("p", "s", "a.csv", { delimiter: ";", encoding: "utf-8-sig", sheet: " " }), "http://localhost").searchParams.has("sheet"), false);
});

test("original download only accepts the private same-origin route for the active batch", () => {
  assert.equal(privateOriginalUrl({ id: "batch-id", original_url: "/api/v1/imports/batch-id/original" }), "/api/v1/imports/batch-id/original");
  for (const original_url of ["https://external.example/original", "//external.example/original", "/api/v1/imports/other/original", "javascript:alert(1)"]) assert.equal(privateOriginalUrl({ id: "batch-id", original_url }), null);
});

test("reload persistence is user-scoped and stores only selection IDs; unavailable storage is recoverable", () => {
  const values = new Map<string, string>();
  const storage = { getItem: (key: string) => values.get(key) ?? null, setItem: (key: string, value: string) => { values.set(key, value); } };
  saveImportSelection(storage, "member-1", { portfolioId: "portfolio-1", importId: "batch-1" });
  assert.deepEqual(readImportSelection(storage, "member-1"), { portfolioId: "portfolio-1", importId: "batch-1" });
  assert.deepEqual(readImportSelection(storage, "viewer-2"), { portfolioId: "", importId: "" });
  values.set("hub:imports:member-1", "invalid JSON");
  assert.deepEqual(readImportSelection(storage, "member-1"), { portfolioId: "", importId: "" });
  assert.doesNotThrow(() => saveImportSelection({ setItem: () => { throw new Error("disabled"); } }, "member-1", { portfolioId: "p", importId: "i" }));
});
