"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, positionsCsv } from "@/lib/api";
import type { Filters } from "@/lib/types";
import { useLocale } from "./locale";
import { errorText, Icon } from "./ui";

export function SnapshotExport({ filters, snapshotId, refresh }: { filters: Filters; snapshotId: string; refresh: () => void }) {
  const { tr } = useLocale();
  const controller = useRef<AbortController | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  useEffect(() => () => controller.current?.abort(), []);

  async function download() {
    if (controller.current) return;
    const current = new AbortController();
    controller.current = current;
    setBusy(true); setError(undefined);
    try {
      const blob = await positionsCsv(filters, snapshotId, current.signal);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url; link.download = `posicoes-${filters.as_of}.csv`;
      document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (cause) {
      if (!current.signal.aborted) setError(cause);
    } finally {
      if (!current.signal.aborted) setBusy(false);
      controller.current = null;
    }
  }

  const changed = error instanceof ApiError && error.status === 409;
  return <div className="export-control"><button className="button secondary" onClick={download} disabled={busy || changed}>{busy ? <span className="spinner" /> : <Icon name="download" size={16} />}{busy ? tr("Preparando CSV…", "Preparing CSV…") : tr("Exportar posições", "Export positions")}</button>
    {error !== undefined && <div className="export-error" role="alert"><p>{changed ? tr("Os dados mudaram desde esta consulta. Atualize o painel antes de exportar.", "Data has changed since this view. Refresh the dashboard before exporting.") : errorText(error, tr)}</p>{changed && <button className="text-link" onClick={refresh}>{tr("Atualizar painel", "Refresh dashboard")} <Icon name="refresh" size={14} /></button>}</div>}
  </div>;
}
