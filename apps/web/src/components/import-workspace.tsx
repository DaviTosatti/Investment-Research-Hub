"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { allPages, api, ApiError } from "@/lib/api";
import { date, eventLabels, label, money, number, unitPrice } from "@/lib/format";
import {
  canConfirmImport, importConfigIssue, importConfigSignature, importCsvTemplate, importFileIssue, importPageSize,
  importUploadPath, initialImportConfig, privateOriginalUrl, readImportSelection, saveImportSelection,
  updateRowDecision, updateRowEdit, type ConfigIssue, type ImportSelection,
} from "@/lib/import-config";
import {
  importFields, type ImportBatch, type ImportConfig, type ImportDetail, type ImportField,
  type ImportPreview, type ImportReceipt, type ImportRow, type ImportSnapshot, type ImportSource,
  type ImportStatus, type ImportSummary, type ParseOptions,
} from "@/lib/import-types";
import type { EventType, PageResult, Portfolio } from "@/lib/types";
import { useResource } from "@/lib/use-resource";
import { useHub } from "./hub-shell";
import { useLocale } from "./locale";
import { EmptyState, ErrorState, Field, Icon, LoadingState, Notice, Pagination, Panel, errorText } from "./ui";

const fieldLabels: Record<ImportField, [string, string]> = {
  event_type: ["Tipo de evento", "Event type"], trade_date: ["Data da operação", "Trade date"],
  settlement_date: ["Data de liquidação", "Settlement date"], ticker: ["Ticker", "Ticker"],
  exchange: ["Mercado", "Exchange"], instrument_id: ["ID do instrumento", "Instrument ID"],
  quantity: ["Quantidade / fator", "Quantity / factor"], unit_price: ["Preço unitário", "Unit price"],
  gross_amount: ["Valor bruto", "Gross amount"], fees: ["Taxas", "Fees"], taxes: ["Tributos", "Taxes"],
  external_id: ["Referência externa", "External reference"], notes: ["Observações", "Notes"], currency: ["Moeda", "Currency"],
};
const statusLabels: Record<ImportStatus, [string, string]> = {
  ready: ["Pronta", "Ready"], duplicate: ["Duplicata identificada", "Identified duplicate"],
  needs_review: ["Exige decisão", "Decision required"], quarantined: ["Em quarentena", "Quarantined"], excluded: ["Excluída por decisão", "Explicitly excluded"],
};
const configMessages: Record<ConfigIssue, [string, string]> = {
  required_mapping: ["Mapeie o tipo de evento e a data da operação.", "Map the event type and trade date."],
  missing_column: ["Escolha somente colunas presentes neste arquivo.", "Select columns present in this file."],
  repeated_column: ["Uma coluna só pode corresponder a um campo. Revise o mapeamento.", "A column can map to only one field. Review the mapping."],
  reason: ["Cada correção e decisão precisa de um motivo de 5 a 500 caracteres.", "Each correction and decision needs a reason of 5 to 500 characters."],
  exchange: ["Informe um mercado com até 24 caracteres.", "Enter an exchange of up to 24 characters."],
  row: ["Revise as alterações: somente uma correção e uma decisão por linha.", "Review the changes: only one correction and one decision per row."],
  edit_value: ["Cada valor corrigido pode ter até 2.000 caracteres.", "Each corrected value can have up to 2,000 characters."],
  event_values: ["Mapeie no máximo 40 tipos de evento do arquivo.", "Map at most 40 event names from the file."],
};

// A write may finish on the server after navigation. Only its still-mounted scope
// can apply the response; a synchronous guard also blocks double submissions.
function useImportWrite(canWrite: boolean) {
  const active = useRef(false);
  const guard = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  async function run<T>(task: () => Promise<T>, accept: (result: T) => void, failure?: (cause: unknown) => void) {
    if (!canWrite || guard.current || !active.current) return;
    guard.current = true; setBusy(true); setError(undefined);
    try { const result = await task(); if (active.current) accept(result); }
    catch (cause) { if (active.current) { setError(cause); failure?.(cause); } }
    finally { guard.current = false; if (active.current) setBusy(false); }
  }
  return { busy, error, run };
}

export function ImportWorkspace() {
  const { user, filters } = useHub();
  return <section id="importacoes" className="import-workspace" aria-label="Import CSV / XLSX" tabIndex={-1}>
    <ImportScope key={`${user.id}:${filters.owner_id}:${filters.portfolio_id}`} />
  </section>;
}

function ImportScope() {
  const { user, filters, references, referencesLoading, referencesError, refresh, canWrite } = useHub();
  const { tr } = useLocale();
  const [selection, setSelection] = useState<ImportSelection>();
  const restore = useCallback(async () => {
    try { return readImportSelection(window.localStorage, user.id); }
    catch { return { portfolioId: "", importId: "" }; }
  }, [user.id]);
  const saved = useResource(`import-selection:${user.id}`, restore);
  const chosen = selection ?? saved.data;
  const portfolios = references?.portfolios.filter(portfolio => !filters.owner_id || portfolio.owner_id === filters.owner_id) ?? [];
  const portfolioId = filters.portfolio_id || chosen?.portfolioId || "";
  const portfolio = portfolios.find(item => item.id === portfolioId);
  const importId = chosen && portfolio && chosen.portfolioId === portfolio.id ? chosen.importId : "";
  function choose(next: ImportSelection) {
    setSelection(next);
    try { saveImportSelection(window.localStorage, user.id, next); } catch { /* Server history is still available. */ }
  }
  return <>
    <Panel title={tr("Importar operações", "Import transactions")} subtitle={tr("CSV ou XLSX · Original preservado · Confirmação após conferência", "CSV or XLSX · Original preserved · Confirm after review")} action={<span className="badge neutral">BRL</span>}>
      <div className="import-body">
        <ol className="import-steps" aria-label={tr("Etapas da importação", "Import steps")}><li><span>1</span>{tr("Escolher arquivo", "Choose file")}</li><li><span>2</span>{tr("Mapear colunas", "Map columns")}</li><li><span>3</span>{tr("Revisar e confirmar", "Review & confirm")}</li></ol>
        <Field label={tr("Conta / carteira · titular", "Account / portfolio · owner")} hint={tr("O arquivo pertence a uma carteira. O histórico de importações inclui todas as datas dessa carteira.", "A file belongs to one portfolio. Import history includes all dates for that portfolio.")}>
          <select value={portfolio?.id ?? ""} disabled={referencesLoading || saved.loading || !!filters.portfolio_id} onChange={event => choose({ portfolioId: event.target.value, importId: "" })}>
            <option value="">{tr("Selecione o destino", "Select a destination")}</option>
            {portfolios.map(item => <option key={item.id} value={item.id}>{item.account_name} · {item.name} · {item.owner_name}</option>)}
          </select>
        </Field>
        {!canWrite && <Notice>{tr("Perfil de leitura: consulte arquivos, prévias e recibos. Importar, corrigir e confirmar requer perfil de membro ou administrador.", "Read-only role: browse files, previews and receipts. Uploading, correcting and confirming requires a member or administrator role.")}</Notice>}
        {referencesError !== undefined ? <ErrorState error={referencesError} retry={refresh} /> : referencesLoading || saved.loading ? <LoadingState /> : !portfolios.length ? <EmptyState icon="wallet" title={tr("Nenhuma carteira disponível", "No portfolio available")} description={tr("Cadastre uma carteira com conta e titular para importar operações.", "Create a portfolio with an account and owner to import transactions.")} action={<Link className="text-link" href="/carteiras">{tr("Abrir carteiras", "Open portfolios")} →</Link>} /> : !portfolio && <p className="muted">{tr("Escolha uma carteira para enviar um arquivo ou retomar uma importação.", "Choose a portfolio to upload a file or resume an import.")}</p>}
      </div>
    </Panel>
    {portfolio && <PortfolioImports key={portfolio.id} portfolio={portfolio} importId={importId} select={id => choose({ portfolioId: portfolio.id, importId: id })} />}
  </>;
}

function PortfolioImports({ portfolio, importId, select }: { portfolio: Portfolio; importId: string; select: (id: string) => void }) {
  const { tr, language } = useLocale();
  const { revision, canWrite } = useHub();
  const [offset, setOffset] = useState(0);
  const [reload, setReload] = useState(0);
  const [historyRevision, setHistoryRevision] = useState(0);
  const loadHistory = useCallback((signal: AbortSignal) => api<PageResult<ImportBatch>>(`/imports?portfolio_id=${encodeURIComponent(portfolio.id)}&limit=10&offset=${offset}`, { signal }), [portfolio.id, offset]);
  const history = useResource(`imports:${portfolio.id}:${offset}:${revision}:${reload}:${historyRevision}`, loadHistory);
  const loadBatch = useCallback(async (signal: AbortSignal) => {
    const batch = await api<ImportDetail>(`/imports/${encodeURIComponent(importId)}`, { signal });
    if (batch.portfolio_id !== portfolio.id || batch.id !== importId) throw new ApiError(409, "IMPORT_CONTEXT", tr("Este arquivo pertence a outra carteira. Selecione-o no histórico correto.", "This file belongs to another portfolio. Select it from the appropriate history."));
    return batch;
    // tr only translates an error; it does not identify this resource.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [importId, portfolio.id]);
  const detail = useResource(importId ? `import:${portfolio.id}:${importId}:${revision}:${reload}` : null, loadBatch);
  const retry = () => setReload(value => value + 1);
  return <>
    <Panel title={tr("Arquivos e histórico", "Files & history")} subtitle={`${portfolio.owner_name} · ${portfolio.account_name} · ${portfolio.name}`} action={importId && <button className="button secondary small-button" onClick={() => select("")}>{canWrite ? tr("Novo arquivo", "New file") : tr("Fechar arquivo", "Close file")}</button>}>
      {history.loading ? <LoadingState /> : history.error !== undefined ? <ErrorState error={history.error} retry={retry} /> : history.data && <>
        {!history.data.items.length ? <div className="import-body"><p className="muted">{tr("Nenhum arquivo enviado para esta carteira.", "No files uploaded for this portfolio.")}</p></div> : <ul className="import-file-list">{history.data.items.map(batch => <li key={batch.id}><button className="import-file-button" aria-pressed={importId === batch.id} onClick={() => { if (importId === batch.id) retry(); else select(batch.id); }}><span><strong>{batch.filename}</strong><small>{batch.source_name} · {date(batch.created_at, language, true)}</small></span><span className={`badge ${batch.status === "committed" ? "valid" : "neutral"}`}>{batch.status === "committed" ? tr("Confirmado", "Confirmed") : batch.status === "previewed" ? tr("Em revisão", "In review") : tr("A mapear", "To map")}</span><Icon name="chevron" size={16} /></button></li>)}</ul>}
        <Pagination total={history.data.total} offset={offset} limit={10} change={setOffset} />
      </>}
    </Panel>
    {!importId ? canWrite && <UploadImport key="upload" portfolio={portfolio} accepted={batch => { setOffset(0); retry(); select(batch.id); }} /> : detail.loading ? <LoadingState /> : detail.error !== undefined ? <ErrorState error={detail.error} retry={retry} /> : detail.data && <BatchWorkspace key={detail.data.id} batch={detail.data} portfolio={portfolio} reload={retry} changed={() => setHistoryRevision(value => value + 1)} />}
  </>;
}

function UploadImport({ portfolio, accepted }: { portfolio: Portfolio; accepted: (batch: ImportDetail) => void }) {
  const { canWrite } = useHub();
  const { tr } = useLocale();
  const write = useImportWrite(canWrite);
  const [sourceRevision, setSourceRevision] = useState(0);
  const loadSources = useCallback((signal: AbortSignal) => allPages<ImportSource>("/sources", signal), []);
  const sources = useResource(`import-sources:${sourceRevision}`, loadSources);
  const [sourceId, setSourceId] = useState("");
  const [sourceName, setSourceName] = useState("");
  const [creatingSource, setCreatingSource] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [options, setOptions] = useState<ParseOptions>({ delimiter: ";", encoding: "utf-8-sig", sheet: null });
  const issue = file ? importFileIssue(file) : null;
  const xlsx = file?.name.toLowerCase().endsWith(".xlsx");
  const fileMessages = {
    type: tr("Escolha um arquivo .csv ou .xlsx.", "Choose a .csv or .xlsx file."),
    size: tr("O arquivo excede 2 MiB.", "The file exceeds 2 MiB."), empty: tr("O arquivo está vazio.", "The file is empty."),
    name: tr("Use um nome de arquivo de até 180 caracteres, sem caminho ou caracteres de controle.", "Use a filename of up to 180 characters, without a path or control characters."),
  };
  function upload(event: FormEvent) {
    event.preventDefault();
    if (!file || issue || !sources.data?.some(source => source.id === sourceId) || creatingSource) return;
    void write.run(() => api<ImportDetail>(importUploadPath(portfolio.id, sourceId, file.name, { ...options, sheet: xlsx ? options.sheet : null }), { method: "POST", headers: { "Content-Type": "application/octet-stream" }, body: file }), accepted);
  }
  function downloadTemplate() {
    const url = URL.createObjectURL(new Blob([importCsvTemplate(options.delimiter)], { type: "text/csv;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url; anchor.download = "hub-import-template.csv"; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  return <Panel title={tr("1. Enviar arquivo", "1. Upload file")} subtitle={tr("Até 2 MiB, 500 linhas de dados e 40 colunas · Nenhuma operação será registrada nesta etapa", "Up to 2 MiB, 500 data rows and 40 columns · No transactions are recorded at this step")}>
    <div className="import-body">
      <p className="muted small">{tr("Processamento síncrono e limitado, sem tarefas em segundo plano.", "Bounded synchronous processing, with no background jobs.")} <button type="button" className="text-link import-inline-action" onClick={downloadTemplate}>{tr("Baixar modelo CSV (só cabeçalhos)", "Download CSV template (headers only)")}</button></p>
      {sources.error !== undefined && <ErrorState error={sources.error} retry={() => setSourceRevision(value => value + 1)} />}
      {sources.loading && <LoadingState />}
      <form onSubmit={upload}><fieldset disabled={!canWrite || write.busy}>
        <Field label={tr("Fonte do arquivo", "File source")} hint={tr("Selecione a instituição ou origem responsável pelo extrato.", "Select the institution or source responsible for the statement.")}><select value={sourceId} disabled={sources.loading || !sources.data || creatingSource} required onChange={event => setSourceId(event.target.value)}><option value="">{tr("Selecione uma fonte", "Select a source")}</option>{sources.data?.map(source => <option key={source.id} value={source.id}>{source.name}</option>)}</select></Field>
        <button type="button" className="text-link import-inline-action" aria-expanded={creatingSource} onClick={() => setCreatingSource(value => !value)}>{creatingSource ? tr("Usar fonte existente", "Use existing source") : tr("Cadastrar fonte", "Create source")}</button>
        {creatingSource && <div className="import-source-create"><Field label={tr("Nome da nova fonte", "New source name")}><input value={sourceName} maxLength={120} onChange={event => setSourceName(event.target.value)} /></Field><button type="button" className="button secondary" disabled={!sourceName.trim()} onClick={() => void write.run(() => api<ImportSource>("/sources", { method: "POST", body: JSON.stringify({ name: sourceName.trim() }) }), source => { setSourceId(source.id); setSourceRevision(value => value + 1); setCreatingSource(false); setSourceName(""); })}>{tr("Salvar fonte", "Save source")}</button></div>}
        <Field label={tr("Arquivo CSV ou XLSX", "CSV or XLSX file")} hint={tr("O original completo é preservado com acesso privado.", "The complete original is preserved with private access.")}><input type="file" accept=".csv,.xlsx" required onChange={event => setFile(event.target.files?.[0] ?? null)} /></Field>
        {issue && <p className="form-error" role="alert">{fileMessages[issue]}</p>}
        <details className="import-details" open={!!file}><summary>{tr("Opções de leitura", "Reading options")}</summary><div className="import-grid">
          {xlsx ? <Field label={tr("Aba (opcional)", "Sheet (optional)")} hint={tr("Vazio usa a primeira aba. Informe o nome exato para escolher outra.", "Leave blank to use the first sheet. Enter an exact name to choose another.")}><input value={options.sheet ?? ""} maxLength={100} onChange={event => setOptions({ ...options, sheet: event.target.value })} /></Field> : <>
            <Field label={tr("Separador de colunas", "Column delimiter")}><select value={options.delimiter} onChange={event => setOptions({ ...options, delimiter: event.target.value as ParseOptions["delimiter"] })}><option value=";">{tr("Ponto e vírgula (;)", "Semicolon (;)")}</option><option value=",">{tr("Vírgula (,)", "Comma (,)")}</option><option value={"\t"}>Tab</option></select></Field>
            <Field label={tr("Codificação", "Encoding")}><select value={options.encoding} onChange={event => setOptions({ ...options, encoding: event.target.value as ParseOptions["encoding"] })}><option value="utf-8-sig">UTF-8 (BOM)</option><option value="cp1252">Windows-1252</option></select></Field>
          </>}
        </div></details>
        <button className="button primary" type="submit" disabled={!file || !!issue || !sourceId || creatingSource || sources.loading || !sources.data}>{write.busy ? <span className="spinner" /> : <Icon name="arrow" size={16} />}{tr("Enviar e conferir amostra", "Upload & inspect sample")}</button>
      </fieldset></form>
      {write.error !== undefined && <p className="form-error" role="alert">{errorText(write.error, tr)}</p>}
    </div>
  </Panel>;
}

function BatchWorkspace({ batch, portfolio, reload, changed }: { batch: ImportDetail; portfolio: Portfolio; reload: () => void; changed: () => void }) {
  const { canWrite, refresh } = useHub();
  const { tr, language } = useLocale();
  const write = useImportWrite(canWrite);
  const [preview, setPreview] = useState(batch.preview);
  const [config, setConfig] = useState<ImportConfig>(batch.preview?.config ?? initialImportConfig(batch.headers));
  const [receipt, setReceipt] = useState(batch.receipt);
  const [reviewed, setReviewed] = useState(!!batch.preview);
  const [acknowledged, setAcknowledged] = useState(false);
  const [stale, setStale] = useState(false);
  const [committedElsewhere, setCommittedElsewhere] = useState(false);
  const [snapshotId, setSnapshotId] = useState("");
  const [snapshotRevision, setSnapshotRevision] = useState(0);
  const [snapshotRetry, setSnapshotRetry] = useState(0);
  const previewFocus = useRef<HTMLDivElement>(null);
  const generated = useRef(false);
  const loadSnapshot = useCallback(async (signal: AbortSignal) => {
    const result = await api<ImportPreview>(`/snapshots/${encodeURIComponent(snapshotId)}`, { signal });
    if (result.import_id !== batch.id || result.id !== snapshotId) throw new ApiError(409, "IMPORT_CONTEXT", "");
    return result;
  }, [snapshotId, batch.id]);
  const snapshot = useResource(snapshotId ? `import-snapshot:${batch.id}:${snapshotId}:${snapshotRetry}` : null, loadSnapshot);
  const displayed = snapshotId ? snapshot.data : preview;
  const dirty = !preview || importConfigSignature(config) !== importConfigSignature(preview.config);
  const issue = importConfigIssue(config, batch.headers);
  const locked = !canWrite || write.busy || !!receipt || committedElsewhere || !!snapshotId;
  const original = privateOriginalUrl(batch);
  const canConfirm = canConfirmImport({ importId: batch.id, latestPreviewId: preview?.id ?? null, preview, config, canWrite, pending: write.busy, historical: !!snapshotId, stale, committed: !!receipt || committedElsewhere, acknowledged: acknowledged && reviewed });
  function changeConfig(next: ImportConfig, mapping = false) {
    if (locked) return;
    setConfig(next); setAcknowledged(false);
    if (mapping) setReviewed(false);
  }
  function failed(cause: unknown) {
    if (cause instanceof ApiError && cause.status === 409) {
      setStale(true); setAcknowledged(false);
      if (cause.code === "IMPORT_COMMITTED") setCommittedElsewhere(true);
    }
  }
  function generate(event: FormEvent) {
    event.preventDefault();
    if (locked || issue || !reviewed) return;
    void write.run(() => api<ImportPreview>(`/imports/${encodeURIComponent(batch.id)}/preview`, { method: "POST", body: JSON.stringify(config) }), result => {
      generated.current = true;
      setPreview(result); setConfig(result.config); setStale(false); setAcknowledged(false);
      setSnapshotRevision(value => value + 1);
      changed();
    }, failed);
  }
  function confirm() {
    if (!canConfirm || !preview) return;
    void write.run(() => api<ImportReceipt>(`/imports/${encodeURIComponent(batch.id)}/confirm`, { method: "POST", body: JSON.stringify({ preview_id: preview.id }) }), result => {
      setReceipt(result); setAcknowledged(false); refresh();
    }, failed);
  }
  useEffect(() => {
    if (generated.current) { previewFocus.current?.focus(); generated.current = false; }
  }, [preview?.id]);
  useEffect(() => {
    if (!dirty || !preview || receipt) return;
    const warn = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ""; };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, preview, receipt]);
  return <div className="import-batch" aria-busy={write.busy}>
    <Panel title={batch.filename} subtitle={`${portfolio.owner_name} · ${portfolio.account_name} · ${portfolio.name} · ${batch.source_name}`} action={original && <a className="button secondary small-button" href={original} download><Icon name="download" size={15} />{tr("Original", "Original")}</a>}>
      <div className="import-body">
        <p className="import-file-meta">{batch.row_count} {tr("linhas", "rows")} · {batch.headers.length} {tr("colunas", "columns")} · {date(batch.created_at, language, true)}</p>
        <details className="import-details"><summary>{tr("Procedência e leitura do original", "Original provenance & reading options")}</summary><dl className="import-evidence"><div><dt>{tr("Importação", "Import")}</dt><dd><code>{batch.id}</code></dd></div><div><dt>SHA-256</dt><dd><code>{batch.sha256}</code></dd></div><div><dt>{tr("Autor (ID)", "Author (ID)")}</dt><dd><code>{batch.created_by}</code></dd></div><div><dt>{tr("Leitura", "Reading")}</dt><dd>{batch.size} bytes · {batch.parse_options.encoding} · {batch.parse_options.delimiter === "\t" ? "Tab" : batch.parse_options.delimiter} · {batch.parse_options.sheet ?? tr("Primeira aba (XLSX)", "First sheet (XLSX)")}</dd></div></dl></details>
        <details className="import-details" open={!preview}><summary>{tr("Amostra original", "Original sample")} · {batch.sample.length} / {batch.row_count} {tr("linhas", "rows")}</summary>
          <p className="muted small">{tr("Confira cabeçalhos, datas e separadores antes de gerar a prévia.", "Inspect headers, dates and separators before generating the preview.")}</p>
          <div className="table-scroll import-sample" tabIndex={0} role="region" aria-label={tr("Amostra do arquivo com rolagem horizontal", "File sample with horizontal scrolling")}><table><caption className="sr-only">{tr("Valores originais, sem alterações", "Original, unchanged values")}</caption><thead><tr><th>{tr("Linha", "Row")}</th>{batch.headers.map(header => <th key={header} scope="col">{header}</th>)}<th>{tr("Leitura", "Reading")}</th></tr></thead><tbody>{batch.sample.map(row => <tr key={row.number}><th scope="row">{row.number}</th>{batch.headers.map(header => <td key={header}>{row.values[header] === null || row.values[header] === "" ? <span className="muted">{tr("Vazio", "Empty")}</span> : row.values[header]}</td>)}<td>{row.errors.join(" · ") || "—"}</td></tr>)}</tbody></table></div>
        </details>
      </div>
    </Panel>
    {receipt && <ReceiptPanel receipt={receipt} />}
    {snapshotId && <Notice>{tr("Revisão histórica aberta: o mapeamento e as linhas abaixo são somente para consulta.", "Historical revision open: the mapping and rows below are read only.")}</Notice>}
    <Panel title={snapshotId ? tr("Mapeamento da revisão histórica", "Historical revision mapping") : tr("2. Mapear e interpretar", "2. Map & interpret")} subtitle={tr("Sugestões apenas para nomes de colunas idênticos aos campos · Revise antes de continuar", "Suggestions use exact canonical column names only · Review before continuing")}>
      <form id="import-preview-config" className="import-body" onSubmit={generate}>
        <fieldset disabled={locked}>
          {snapshotId && snapshot.loading ? <LoadingState /> : <MappingFields batch={batch} config={snapshotId && snapshot.data ? snapshot.data.config : config} change={next => changeConfig(next, true)} />}
          {!snapshotId && <>
          <label className="import-checkbox"><input type="checkbox" checked={reviewed} onChange={event => setReviewed(event.target.checked)} /><span>{tr("Conferi a amostra, o mapeamento e os formatos.", "I reviewed the sample, mapping and formats.")}</span></label>
          {issue && <p className="form-context" role="status">{tr(...configMessages[issue])}</p>}
          <div className="import-actions"><button className="button primary" type="submit" disabled={!reviewed || !!issue}>{write.busy ? <span className="spinner" /> : <Icon name="refresh" size={16} />}{preview ? tr("Gerar nova prévia", "Generate new preview") : tr("Gerar prévia", "Generate preview")}</button>{preview && dirty && <button type="button" className="button secondary" onClick={() => { setConfig(preview.config); setReviewed(true); setAcknowledged(false); }}>{tr("Desfazer alterações locais", "Discard local changes")}</button>}</div>
          </>}
        </fieldset>
        {dirty && preview && !snapshotId && <p className="import-pending" role="status">{tr("Há alterações locais. A prévia abaixo ainda mostra a revisão anterior; gere uma nova para salvar e confirmar. Sair deste arquivo descarta alterações ainda não salvas.", "There are local changes. The preview below still shows the previous revision; generate a new one to save and confirm. Leaving this file discards unsaved changes.")}</p>}
      </form>
    </Panel>
    {write.error !== undefined && <div className="import-feedback" role="alert"><p className="form-error">{errorText(write.error, tr)}</p>{stale && <p>{committedElsewhere ? tr("Uma revisão já foi confirmada. Atualize para consultar o recibo.", "A revision has already been confirmed. Refresh to view its receipt.") : tr("A prévia ficou desatualizada. Gere uma nova prévia e confira os resultados antes de confirmar novamente.", "This preview is stale. Generate a new preview and review the results before confirming again.")}</p>}{committedElsewhere && <button className="button secondary" onClick={reload}>{tr("Consultar estado atual", "Load current state")}</button>}</div>}
    <SnapshotHistory importId={batch.id} revision={snapshotRevision} selectedId={snapshotId} select={id => { setSnapshotId(id); setAcknowledged(false); }} />
    {snapshotId && <Notice>{tr("Revisão histórica: consulta somente. Ela não pode ser confirmada nem substituir suas alterações atuais.", "Historical revision: read only. It cannot be confirmed or replace your current changes.")} <button className="text-link import-inline-action" onClick={() => setSnapshotId("")}>{tr("Voltar à prévia atual", "Return to current preview")}</button></Notice>}
    {snapshotId && snapshot.loading ? <LoadingState /> : snapshotId && snapshot.error !== undefined ? <ErrorState error={snapshot.error} retry={() => setSnapshotRetry(value => value + 1)} /> : displayed ? <>
      <div ref={previewFocus} tabIndex={-1} className="import-preview-focus" aria-label={tr("Revisão da importação", "Import review")}><Panel title={tr("3. Revisar linhas", "3. Review rows")} subtitle={`${tr("Revisão", "Revision")} ${displayed.revision} · ${date(displayed.created_at, language, true)}`}>
        <PreviewSummary summary={displayed.summary} />
        <ReviewRows key={displayed.id} preview={displayed} config={snapshotId ? displayed.config : config} change={changeConfig} readOnly={locked} />
        {dirty && !snapshotId && !receipt && <div className="import-body">{issue && <p className="import-pending" role="status">{tr(...configMessages[issue])}</p>}<button className="button primary" type="submit" form="import-preview-config" disabled={locked || !!issue || !reviewed}>{tr("Gerar prévia com alterações", "Preview these changes")}</button></div>}
      </Panel></div>
      {!snapshotId && !receipt && <Panel title={tr("Confirmar esta prévia", "Confirm this preview")} subtitle={tr("Somente as linhas prontas criam operações. Duplicatas reconhecidas reutilizam o registro; exclusões preservam a decisão.", "Only ready rows create transactions. Identified duplicates reuse their record; exclusions preserve your decision.")}>
        <div className="import-body">
          {!preview?.summary.can_commit && <Notice tone="warning">{tr("Confira cada linha que exige decisão. Em quarentena, corrija os valores ou exclua a linha com motivo; depois gere uma nova prévia. Nenhuma linha pendente é descartada automaticamente.", "Review each row requiring a decision. For quarantined rows, correct the values or explicitly exclude with a reason, then generate a new preview. Pending rows are never silently discarded.")}</Notice>}
          <fieldset disabled={locked || dirty || stale || !preview?.summary.can_commit}>
            <label className="import-checkbox"><input type="checkbox" checked={acknowledged} onChange={event => setAcknowledged(event.target.checked)} /><span>{tr("Conferi os valores, duplicatas e exclusões desta revisão. Confirmo que representam fatos econômicos já realizados.", "I reviewed the values, duplicates and exclusions in this revision. I confirm these are completed economic events.")}</span></label>
            <button type="button" className="button primary" disabled={!canConfirm} onClick={confirm}>{write.busy ? <span className="spinner" /> : <Icon name="check" size={16} />}{tr("Confirmar importação", "Confirm import")}</button>
          </fieldset>
        </div>
      </Panel>}
    </> : <Panel title={tr("Prévia ainda não gerada", "No preview yet")}><div className="import-body"><p className="muted">{tr("Confira a amostra e o mapeamento para visualizar o efeito no caixa e a qualidade de cada linha.", "Review the sample and mapping to inspect the cash impact and each row’s quality.")}</p></div></Panel>}
  </div>;
}

function MappingFields({ batch, config, change }: { batch: ImportDetail; config: ImportConfig; change: (config: ImportConfig) => void }) {
  const { tr } = useLocale();
  const primary: ImportField[] = ["event_type", "trade_date", "ticker", "quantity", "unit_price", "gross_amount"];
  const field = (name: ImportField) => <Field key={name} label={`${tr(...fieldLabels[name])}${name === "event_type" || name === "trade_date" ? " *" : ""}`} hint={name}>
    <select value={config.mapping[name] ?? ""} required={name === "event_type" || name === "trade_date"} onChange={event => {
      const mapping = { ...config.mapping };
      if (event.target.value) mapping[name] = event.target.value; else delete mapping[name];
      change({ ...config, mapping });
    }}><option value="">{tr("Não mapear", "Do not map")}</option>{batch.headers.map(header => <option key={header} value={header}>{header}</option>)}</select>
  </Field>;
  const eventColumn = config.mapping.event_type;
  const rows = batch.preview?.rows.map(row => row.raw) ?? batch.sample.map(row => row.values);
  const eventNames = [...new Set([...Object.keys(config.event_values ?? {}), ...rows.map(row => eventColumn ? row[eventColumn]?.trim() : null).filter((value): value is string => !!value)])].slice(0, 40);
  const aliases: [string, EventType][] = [["aporte", "deposit"], ["retirada", "withdrawal"], ["compra", "buy"], ["venda", "sell"], ["dividendo", "dividend"], ["taxa", "fee"], ["imposto", "tax"], ["desdobramento", "split"]];
  return <>
    <div className="import-grid">{primary.map(field)}</div>
    <details className="import-details"><summary>{tr("Outros campos e referências", "Other fields & references")}</summary><div className="import-grid">{importFields.filter(name => !primary.includes(name)).map(field)}</div></details>
    <div className="import-grid">
      <Field label={tr("Separador decimal", "Decimal separator")}><select value={config.decimal_separator} onChange={event => change({ ...config, decimal_separator: event.target.value as ImportConfig["decimal_separator"] })}><option value=".">{tr("Ponto (1234.56)", "Point (1234.56)")}</option><option value=",">{tr("Vírgula (1234,56)", "Comma (1234,56)")}</option></select></Field>
      <Field label={tr("Formato das datas de texto", "Text date format")}><select value={config.date_format} onChange={event => change({ ...config, date_format: event.target.value as ImportConfig["date_format"] })}><option value="YYYY-MM-DD">YYYY-MM-DD</option><option value="DD/MM/YYYY">DD/MM/YYYY</option></select></Field>
      <Field label={tr("Mercado padrão", "Default exchange")} hint={tr("Usado quando não houver mercado na linha.", "Used when the row has no exchange.")}><input value={config.exchange} required maxLength={24} onChange={event => change({ ...config, exchange: event.target.value })} /></Field>
    </div>
    <p className="import-config-hint">{tr("Números sem separador de milhares ou símbolo monetário. Números e datas mapeados, mas vazios, ficam em quarentena. Sem mapeamento, taxas e tributos usam zero; liquidação usa a data da operação. Desmarque colunas que não se aplicam. Datas e números nativos de XLSX já são reconhecidos.", "Use numbers without grouping or currency symbols. Mapped numbers and dates that are blank are quarantined. Unmapped fees and taxes default to zero; settlement defaults to the trade date. Unmap columns that do not apply. Native XLSX dates and numbers are already recognized.")}</p>
    <details className="import-details"><summary>{tr("Tipos de evento aceitos", "Supported event types")}</summary>
      <p className="muted small">{tr("Use o nome em português ou o código em inglês. São registros realizados, nunca ordens à corretora.", "Use the Portuguese name or English code. These record completed events, never broker orders.")}</p>
      <dl className="import-event-labels">{aliases.map(([pt, en]) => <div key={en}><dt>{pt}</dt><dd><code>{en}</code></dd></div>)}</dl>
      {!!eventNames.length && <details className="import-details"><summary>{tr("Traduzir outros nomes deste arquivo (opcional)", "Translate other names in this file (optional)")}</summary><div className="import-grid">{eventNames.map(value => <Field key={value} label={value}><select value={config.event_values?.[value] ?? ""} onChange={event => {
        const event_values = { ...config.event_values, ...(event.target.value ? { [value]: event.target.value as EventType } : {}) };
        if (!event.target.value) delete event_values[value];
        change({ ...config, event_values });
      }}><option value="">{tr("Usar nomes aceitos acima", "Use supported names above")}</option>{aliases.map(([pt, en]) => <option key={en} value={en}>{pt} → {en}</option>)}</select></Field>)}</div></details>}
    </details>
  </>;
}

function PreviewSummary({ summary }: { summary: ImportSummary }) {
  const { tr, language } = useLocale();
  return <div className="import-body">
    <div className="import-metrics"><div><span>{tr("Caixa antes", "Cash before")} · {summary.currency}</span><strong>{money(summary.cash_before, language)}</strong></div><div><span>{tr("Caixa após linhas prontas", "Cash after ready rows")} · {summary.currency}</span><strong>{money(summary.cash_after, language)}</strong></div><div><span>{tr("Período das linhas interpretadas", "Parsed rows’ period")}</span><strong className="import-period">{summary.period_start ? date(summary.period_start, language) : "—"} → {summary.period_end ? date(summary.period_end, language) : "—"}</strong></div></div>
    <ul className="import-counts" aria-label={tr("Qualidade das linhas", "Row quality")}>{(Object.keys(statusLabels) as ImportStatus[]).map(status => <li key={status}><StatusBadge status={status} /><strong>{summary[status]}</strong></li>)}</ul>
    <p className="muted small">{tr("Valores", "Amounts")}: {summary.amount_unit} · {tr("Quantidade", "Quantity")}: {summary.quantity_unit === "units_or_split_factor" ? tr("unidades ou fator de desdobramento", "units or split factor") : summary.quantity_unit}. {tr("Caixa por data de negociação; valores calculados pelo motor.", "Trade-date cash; amounts calculated by the engine.")}</p>
  </div>;
}

function StatusBadge({ status }: { status: ImportStatus }) {
  const { tr } = useLocale();
  return <span className={`badge import-status-${status}`}>{tr(...statusLabels[status])}</span>;
}

function ReviewRows({ preview, config, change, readOnly }: { preview: ImportPreview; config: ImportConfig; change: (config: ImportConfig) => void; readOnly: boolean }) {
  const { tr, language } = useLocale();
  const [filter, setFilter] = useState<ImportStatus | "all">("all");
  const [offset, setOffset] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const rows = preview.rows.filter(row => filter === "all" || row.status === filter);
  const selectedRow = preview.rows.find(row => row.row_number === selected);
  return <>
    <div className="import-body import-row-toolbar"><Field label={tr("Linhas da prévia", "Preview rows")}><select value={filter} onChange={event => { setFilter(event.target.value as typeof filter); setOffset(0); setSelected(null); }}><option value="all">{tr("Todas as linhas", "All rows")} ({preview.rows.length})</option>{(Object.keys(statusLabels) as ImportStatus[]).map(status => <option key={status} value={status}>{tr(...statusLabels[status])} ({preview.summary[status]})</option>)}</select></Field><p className="muted small">{tr("Semelhança não comprova duplicidade. Examine as referências antes de decidir.", "Similarity does not establish duplication. Inspect the references before deciding.")}</p></div>
    {rows.length ? <div className="table-scroll"><table className="responsive-table import-rows"><caption className="sr-only">{tr("Prévia das operações por linha do original", "Preview of transactions by original row")}</caption><thead><tr><th>{tr("Linha", "Row")}</th><th>{tr("Qualidade", "Quality")}</th><th>{tr("Evento / data", "Event / date")}</th><th className="numeric">{tr("Valor bruto (BRL)", "Gross amount (BRL)")}</th><th>{tr("Conferência", "Review")}</th></tr></thead><tbody>{rows.slice(offset, offset + importPageSize).map(row => {
      const pending = JSON.stringify(config.edits.find(edit => edit.row_number === row.row_number)) !== JSON.stringify(preview.config.edits.find(edit => edit.row_number === row.row_number)) || JSON.stringify(config.decisions.find(decision => decision.row_number === row.row_number)) !== JSON.stringify(preview.config.decisions.find(decision => decision.row_number === row.row_number));
      return <tr key={row.row_number} className={selected === row.row_number ? "import-selected-row" : undefined}><td data-label={tr("Linha", "Row")}><strong>{row.row_number}</strong></td><td data-label={tr("Qualidade", "Quality")}><StatusBadge status={row.status} />{pending && <span className="cell-secondary">{tr("Alteração a aplicar", "Pending change")}</span>}</td><td data-label={tr("Evento / data", "Event / date")}>{row.normalized ? <><strong>{label(eventLabels, row.normalized.event_type ?? "", language)}</strong><span className="cell-secondary">{date(row.normalized.trade_date, language)}</span></> : "—"}</td><td data-label={tr("Valor bruto", "Gross amount")} className="numeric">{row.normalized?.event_type === "split" ? tr("Sem fluxo de caixa", "No cash flow") : money(row.calculated_gross_amount, language)}</td><td data-label={tr("Conferência", "Review")}><button className="button secondary small-button" aria-expanded={selected === row.row_number} aria-controls="import-row-review" onClick={() => setSelected(selected === row.row_number ? null : row.row_number)}>{tr("Conferir", "Inspect")} {row.row_number}</button></td></tr>;
    })}</tbody></table></div> : <div className="import-body"><p className="muted">{tr("Nenhuma linha com este estado.", "No rows with this status.")}</p></div>}
    <Pagination total={rows.length} offset={offset} limit={importPageSize} change={next => { setOffset(next); setSelected(null); }} />
    {selectedRow && <RowInspector key={selectedRow.row_number} row={selectedRow} config={config} change={change} readOnly={readOnly} />}
  </>;
}

function RowInspector({ row, config, change, readOnly }: { row: ImportRow; config: ImportConfig; change: (config: ImportConfig) => void; readOnly: boolean }) {
  const { tr, language } = useLocale();
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => { heading.current?.focus(); }, []);
  const edit = config.edits.find(item => item.row_number === row.row_number);
  const decision = config.decisions.find(item => item.row_number === row.row_number);
  function editField(field: ImportField, value: string) {
    change(updateRowEdit(config, { row_number: row.row_number, values: { ...edit?.values, [field]: value === "" ? null : value }, reason: edit?.reason ?? "" }, row.row_number));
  }
  function displayValue(field: ImportField, value: string | null | undefined) {
    if (value === null || value === undefined || value === "") return tr("Vazio / ausente", "Empty / absent");
    if (field === "trade_date" || field === "settlement_date") return date(value, language);
    if (field === "event_type") return `${label(eventLabels, value, language)} (${value})`;
    if (field === "unit_price") return unitPrice(value, language);
    if (field === "quantity") return number(value, language);
    if (["gross_amount", "fees", "taxes"].includes(field)) return money(value, language);
    return value;
  }
  const canCreate = row.status === "needs_review" || decision?.action === "create";
  return <div className="import-inspector" id="import-row-review">
    <div className="import-inspector-heading"><h3 tabIndex={-1} ref={heading}>{tr("Conferir linha", "Inspect row")} {row.row_number}</h3><StatusBadge status={row.status} /></div>
    {row.errors.length > 0 && <div className="notice warning"><Icon name="alert" /><ul>{row.errors.map((error, index) => <li key={index}>{error}</li>)}</ul></div>}
    {(row.candidate_count > 0 || row.transaction_id || row.duplicate_of_row) && <div className="import-candidates"><h4>{tr("Referências para reconciliação", "Reconciliation references")}</h4><p className="muted small">{tr("Possíveis correspondências", "Possible matches")}: {row.candidate_count}. {tr("Exibindo", "Showing")} {Math.min(20, row.candidates.length)} {tr("referências (máximo 20).", "references (maximum 20).")}</p><ul>{row.candidates.slice(0, 20).map((candidate, index) => <li key={index}>{candidate.transaction_id ? <>{tr("Operação existente", "Existing transaction")}: <code>{candidate.transaction_id}</code></> : <>{tr("Linha neste arquivo", "Row in this file")}: {candidate.row_number}</>}</li>)}{row.transaction_id && <li>{tr("Duplicata do registro", "Duplicate of transaction")}: <code>{row.transaction_id}</code></li>}{row.duplicate_of_row && <li>{tr("Duplicata da linha", "Duplicate of row")}: {row.duplicate_of_row}</li>}</ul><p className="muted small">{tr("Duplicatas identificadas por referência externa reutilizam a operação. Para operações semelhantes sem identidade comprovada, sua decisão é obrigatória.", "Duplicates identified by external reference reuse the transaction. Similar operations without established identity require your decision.")}</p></div>}
    <div className="import-comparison">
      <details className="import-details" open><summary>{tr("Valores originais", "Original values")}</summary><dl className="import-evidence">{Object.entries(row.raw).map(([field, value]) => <div key={field}><dt>{field}</dt><dd>{value === null || value === "" ? tr("Vazio", "Empty") : value}</dd></div>)}</dl></details>
      <details className="import-details" open><summary>{tr("Valores da prévia", "Preview values")}</summary>{row.normalized ? <dl className="import-evidence">{importFields.filter(field => Object.hasOwn(row.normalized!, field)).map(field => <div key={field}><dt>{tr(...fieldLabels[field])}</dt><dd>{displayValue(field, field === "gross_amount" ? row.calculated_gross_amount : row.normalized?.[field])}</dd></div>)}</dl> : <p className="muted small">{tr("Sem valores normalizados nesta revisão. Consulte os erros ou a decisão de exclusão.", "No normalized values in this revision. Inspect the errors or exclusion decision.")}</p>}</details>
    </div>
    <fieldset disabled={readOnly}>
      <div className="import-grid">
        <Field label={tr("Decisão sobre esta linha", "Decision for this row")}><select value={decision?.action ?? ""} onChange={event => change(updateRowDecision(config, event.target.value ? { row_number: row.row_number, action: event.target.value as "skip" | "create", reason: decision?.reason ?? "" } : null, row.row_number))}><option value="">{tr("Sem decisão manual", "No manual decision")}</option><option value="skip">{tr("Excluir desta importação", "Exclude from this import")}</option>{canCreate && <option value="create">{tr("Criar fato econômico distinto", "Create a separate economic event")}</option>}</select></Field>
        {decision && <Field label={tr("Motivo da decisão", "Decision reason")} hint={tr("Obrigatório · 5 a 500 caracteres", "Required · 5 to 500 characters")}><textarea rows={2} minLength={5} maxLength={500} required value={decision.reason} onChange={event => change(updateRowDecision(config, { ...decision, reason: event.target.value }, row.row_number))} /></Field>}
      </div>
      {decision?.action === "create" && <Notice tone="warning">{tr("Criar significa declarar outro fato econômico, mesmo com valores iguais. Justifique por que esta execução é distinta das referências acima.", "Create means declaring a separate economic event, even with identical values. Explain why this execution is distinct from the references above.")}</Notice>}
      {decision?.action === "skip" && <p className="muted small">{tr("A linha não criará uma operação; o original e o motivo permanecem no histórico.", "The row will not create a transaction; the original and reason remain in history.")}</p>}
      {row.status === "quarantined" && decision?.action !== "skip" && <p className="import-pending">{tr("Corrija os campos abaixo ou escolha excluir com motivo. Criar um novo fato não resolve erros de dados.", "Correct the fields below or choose to exclude with a reason. Creating a separate event does not resolve data errors.")}</p>}
      <details className="import-details"><summary>{tr("Corrigir campos antes de confirmar", "Correct fields before confirmation")}{edit ? ` · ${tr("Com correção", "Correction present")}` : ""}</summary>
        <p className="muted small">{tr("Altere apenas os campos necessários. Use os formatos selecionados acima; vazio envia nulo. A correção requer motivo e uma nova prévia, preservando o original.", "Change only the required fields. Use the selected formats above; blank sends null. Corrections require a reason and a new preview, preserving the original.")}</p>
        <fieldset disabled={decision?.action === "skip"}><div className="import-grid">{importFields.map(field => {
          const value = edit && Object.hasOwn(edit.values, field) ? edit.values[field] : config.mapping[field] ? row.raw[config.mapping[field]!] : "";
          return <Field key={field} label={tr(...fieldLabels[field])} hint={field === "trade_date" || field === "settlement_date" ? config.date_format : undefined}>{field === "notes" ? <textarea rows={2} maxLength={2000} value={value ?? ""} onChange={event => editField(field, event.target.value)} /> : <input value={value ?? ""} maxLength={2000} autoComplete="off" onChange={event => editField(field, event.target.value)} />}</Field>;
        })}</div></fieldset>
        {edit && <><Field label={tr("Motivo da correção", "Correction reason")} hint={tr("Obrigatório · 5 a 500 caracteres", "Required · 5 to 500 characters")}><textarea value={edit.reason} minLength={5} maxLength={500} required rows={2} onChange={event => change(updateRowEdit(config, { ...edit, reason: event.target.value }, row.row_number))} /></Field><button type="button" className="button secondary small-button" onClick={() => change(updateRowEdit(config, null, row.row_number))}>{tr("Remover correção desta linha", "Remove this row’s correction")}</button></>}
      </details>
    </fieldset>
    {(edit || decision) && <p className="muted small">{tr("Gere uma nova prévia para aplicar correções e decisões antes da confirmação.", "Generate a new preview to apply corrections and decisions before confirmation.")}</p>}
  </div>;
}

function SnapshotHistory({ importId, revision, selectedId, select }: { importId: string; revision: number; selectedId: string; select: (id: string) => void }) {
  const { tr, language } = useLocale();
  const [offset, setOffset] = useState(0);
  const [retry, setRetry] = useState(0);
  const load = useCallback((signal: AbortSignal) => api<PageResult<ImportSnapshot>>(`/snapshots?import_id=${encodeURIComponent(importId)}&limit=10&offset=${offset}`, { signal }), [importId, offset]);
  const snapshots = useResource(`import-snapshots:${importId}:${revision}:${offset}:${retry}`, load);
  return <details className="import-history"><summary><Icon name="clock" size={16} />{tr("Histórico de prévias", "Preview history")}{snapshots.data && <span className="badge neutral">{snapshots.data.total}</span>}</summary>
    {snapshots.loading ? <LoadingState /> : snapshots.error !== undefined ? <ErrorState error={snapshots.error} retry={() => setRetry(value => value + 1)} /> : snapshots.data && <>
      {!snapshots.data.items.length ? <p className="muted import-body">{tr("As prévias geradas serão preservadas aqui.", "Generated previews will be preserved here.")}</p> : <ul className="import-file-list">{snapshots.data.items.map(item => <li key={item.id}><button className="import-file-button" aria-pressed={selectedId === item.id} onClick={() => select(item.id)}><span><strong>{tr("Revisão", "Revision")} {item.revision}</strong><small>{date(item.created_at, language, true)} · {item.summary.ready} {tr("prontas", "ready")} · {item.summary.quarantined + item.summary.needs_review} {tr("pendentes", "pending")}</small></span><span className="text-link">{tr("Consultar", "View")}</span></button></li>)}</ul>}
      <Pagination total={snapshots.data.total} offset={offset} limit={10} change={setOffset} />
    </>}
  </details>;
}

function ReceiptPanel({ receipt }: { receipt: ImportReceipt }) {
  const { tr, language } = useLocale();
  const [offset, setOffset] = useState(0);
  return <Panel title={tr("Importação confirmada", "Import confirmed")} subtitle={date(receipt.created_at, language, true)} action={<span className="badge valid"><Icon name="check" size={12} />{tr("Recibo", "Receipt")}</span>}>
    <div className="import-body"><p>{tr("Cada linha abaixo mostra o resultado registrado pelo servidor. Consulte as operações para acompanhar a carteira.", "Each row below shows the result recorded by the server. Open transactions to follow the portfolio.")} <Link href="/operacoes" className="text-link">{tr("Ver operações", "View transactions")} →</Link></p><details className="import-details"><summary>{tr("Identificação do recibo", "Receipt identification")}</summary><dl className="import-evidence"><div><dt>{tr("Recibo", "Receipt")}</dt><dd><code>{receipt.id}</code></dd></div><div><dt>{tr("Prévia confirmada", "Confirmed preview")}</dt><dd><code>{receipt.preview_id}</code></dd></div><div><dt>{tr("Autor (ID)", "Author (ID)")}</dt><dd><code>{receipt.created_by}</code></dd></div></dl></details></div>
    <div className="table-scroll"><table className="responsive-table import-receipt"><caption className="sr-only">{tr("Resultado da importação por linha", "Import result by row")}</caption><thead><tr><th>{tr("Linha", "Row")}</th><th>{tr("Resultado", "Result")}</th><th>{tr("ID da operação", "Transaction ID")}</th></tr></thead><tbody>{receipt.results.slice(offset, offset + importPageSize).map(row => <tr key={row.row_number}><td data-label={tr("Linha", "Row")}>{row.row_number}</td><td data-label={tr("Resultado", "Result")}><StatusBadge status={row.status} /></td><td data-label={tr("ID da operação", "Transaction ID")}>{row.transaction_id ? <code className="import-transaction-id">{row.transaction_id}</code> : tr("Sem lançamento", "No transaction")}</td></tr>)}</tbody></table></div>
    <Pagination total={receipt.results.length} offset={offset} limit={importPageSize} change={setOffset} />
  </Panel>;
}
