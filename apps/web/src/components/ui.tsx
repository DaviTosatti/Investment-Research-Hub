"use client";

import { useRef, useState, type ReactNode, type FormEvent } from "react";
import { ApiError } from "@/lib/api";
import { DecimalInputError } from "@/lib/forms";
import { useLocale } from "./locale";

export type IconName = "home" | "wallet" | "arrows" | "database" | "settings" | "menu" | "close" | "chevron" | "refresh" | "plus" | "download" | "logout" | "chart" | "shield" | "clock" | "arrow" | "check" | "alert";
const paths: Record<IconName, string> = {
  home: "M3 10 12 3l9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1Z",
  wallet: "M3 7V5a2 2 0 0 1 2-2h14v4M3 7h17a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H5a2 2 0 0 1-2-2V7Zm18 5h-6v5h6m-3-2.5h.01",
  arrows: "M3 7h17m-4-4 4 4-4 4M21 17H4m4-4-4 4 4 4",
  database: "M20 6c0 2-4 3-8 3S4 8 4 6s4-3 8-3 8 1 8 3Zm0 0v12c0 2-4 3-8 3s-8-1-8-3V6m0 6c0 2 4 3 8 3s8-1 8-3",
  settings: "M4 7h16M4 17h16M8 4v6m8 4v6", menu: "M4 6h16M4 12h16M4 18h16",
  close: "m6 6 12 12M6 18 18 6", chevron: "m9 5 7 7-7 7", refresh: "M20 10a8 8 0 0 0-14-5L3 8m0-5v5h5m-4 6a8 8 0 0 0 14 5l3-3m0 5v-5h-5",
  plus: "M12 5v14M5 12h14", download: "M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5", logout: "M9 4H4v16h5m5-4 4-4-4-4m-6 4h14",
  chart: "M4 3v17h17M7 15l4-5 4 2 5-7", shield: "M12 3 3 7v5c0 5 9 9 9 9s9-4 9-9V7Zm-5 9 3 3 7-7",
  clock: "M12 8v5l3 2m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0", arrow: "M5 12h14m-5-5 5 5-5 5",
  check: "m5 12 4 4L19 6", alert: "m12 3 10 18H2Zm0 5v6m0 3h.01",
};
export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]} /></svg>;
}
export function Brand({ compact = false }: { compact?: boolean }) {
  return <span className="brand"><span className="brand-mark"><svg width="25" height="25" viewBox="0 0 25 25" fill="none" aria-hidden="true"><path d="M4 18V8h5v10m3 0V4h5v14m3 0v-7" stroke="currentColor" strokeWidth="2.5" /><path d="M3 21h19" stroke="currentColor" /></svg></span>{!compact && <span>Investment<span className="brand-sub">RESEARCH HUB</span></span>}</span>;
}
export function PageHeading({ eyebrow, title, description, action }: { eyebrow: string; title: string; description: string; action?: ReactNode }) {
  return <div className="page-heading"><div><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p className="muted page-description">{description}</p></div>{action && <div className="heading-actions">{action}</div>}</div>;
}
export function Panel({ title, subtitle, action, children, className = "" }: { title: string; subtitle?: string; action?: ReactNode; children: ReactNode; className?: string }) {
  return <section className={`panel ${className}`}><div className="panel-heading"><div><h2>{title}</h2>{subtitle && <p className="muted small">{subtitle}</p>}</div>{action}</div>{children}</section>;
}
export function EmptyState({ title, description, action, icon = "chart" }: { title: string; description: string; action?: ReactNode; icon?: IconName }) {
  return <div className="empty-state"><span className="empty-icon"><Icon name={icon} size={24} /></span><h3>{title}</h3><p className="muted">{description}</p>{action}</div>;
}
export function LoadingState() {
  const { tr } = useLocale();
  return <div className="loading-state" role="status"><span className="spinner" />{tr("Consultando os dados…", "Loading data…")}</div>;
}
export function errorText(error: unknown, tr: (pt: string, en: string) => string) {
  if (error instanceof DecimalInputError) return tr("Use vírgula ou ponto decimal, sem separador de milhares, com até 8 casas decimais.", "Use a decimal comma or point, without thousands separators, with up to 8 decimal places.");
  if (error instanceof ApiError && error.code === "incomplete_list") return tr("A lista recebida está incompleta. Atualize os dados para carregar todas as opções.", "The received list is incomplete. Refresh data to load every option.");
  if (error instanceof ApiError && error.status === 401 && error.message === "E-mail ou senha inválidos.") return tr("E-mail ou senha inválidos.", "Invalid email or password.");
  if (error instanceof ApiError && error.status === 401) return tr("Sua sessão expirou. Entre novamente.", "Your session expired. Sign in again.");
  if (error instanceof ApiError && error.status === 403) return tr("Você não tem permissão para esta ação.", "You do not have permission for this action.");
  if (error instanceof ApiError && error.message) return error.message;
  return tr("Não foi possível consultar ou salvar os dados. Verifique a conexão e tente novamente.", "Could not load or save data. Check your connection and try again.");
}
export function ErrorState({ error, retry }: { error: unknown; retry: () => void }) {
  const { tr } = useLocale();
  return <div className="error-state" role="alert"><Icon name="alert" /><div><strong>{tr("Dados indisponíveis", "Data unavailable")}</strong><p>{errorText(error, tr)}</p></div><button className="button secondary small-button" onClick={retry}>{tr("Tentar novamente", "Try again")}</button></div>;
}
export function Notice({ children, tone = "info" }: { children: ReactNode; tone?: "info" | "warning" }) {
  return <div className={`notice ${tone}`}><Icon name={tone === "warning" ? "alert" : "shield"} /><div>{children}</div></div>;
}
export function Freshness({ quality }: { quality: "valid" | "stale" | "unavailable" }) {
  const { tr } = useLocale();
  return <span className={`badge ${quality}`}><Icon name={quality === "valid" ? "check" : quality === "stale" ? "clock" : "alert"} size={12} />{quality === "valid" ? tr("Atual", "Current") : quality === "stale" ? tr("Desatualizada", "Stale") : tr("Sem cotação", "No quote")}</span>;
}
export function Field({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return <label className="field"><span>{label}</span>{children}{hint && <span className="field-hint">{hint}</span>}</label>;
}
export function useMutation() {
  const { tr } = useLocale();
  const guard = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  const [success, setSuccess] = useState("");
  async function run(event: FormEvent<HTMLFormElement>, task: (form: HTMLFormElement) => Promise<void>, message: string) {
    event.preventDefault();
    if (guard.current) return;
    guard.current = true;
    setBusy(true); setError(undefined); setSuccess("");
    const form = event.currentTarget;
    try { await task(form); setSuccess(message); }
    catch (cause) { setError(cause); }
    finally { guard.current = false; setBusy(false); }
  }
  return { busy, run, feedback: <>{error !== undefined && <p className="form-error" role="alert">{errorText(error, tr)}</p>}{success && <p className="form-success" role="status"><Icon name="check" />{success}</p>}</> };
}
export function Submit({ busy, children }: { busy: boolean; children: ReactNode }) {
  const { tr } = useLocale();
  return <button type="submit" className="button primary" disabled={busy}>{busy ? <><span className="spinner" />{tr("Salvando…", "Saving…")}</> : <><Icon name="plus" size={16} />{children}</>}</button>;
}
export function Pagination({ total, offset, limit, change }: { total: number; offset: number; limit: number; change: (offset: number) => void }) {
  const { tr } = useLocale();
  return <nav className="pagination" aria-label={tr("Paginação", "Pagination")}><span className="muted small">{total === 0 ? "0" : `${offset + 1}–${Math.min(offset + limit, total)}`} / {total}</span><div><button className="button secondary small-button" disabled={offset === 0} onClick={() => change(Math.max(0, offset - limit))}>{tr("Anterior", "Previous")}</button><button className="button secondary small-button" disabled={offset + limit >= total} onClick={() => change(offset + limit)}>{tr("Próxima", "Next")}</button></div></nav>;
}
