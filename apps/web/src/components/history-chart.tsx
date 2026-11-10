"use client";

import { useId, useState } from "react";
import type { Dashboard } from "@/lib/types";
import { date, money, locale } from "@/lib/format";
import { useLocale } from "./locale";
import { EmptyState } from "./ui";

// Number conversion here is exclusively for SVG coordinates; the API owns every financial value.
export function HistoryChart({ history }: { history: Dashboard["history"] }) {
  const { language, tr } = useLocale();
  const id = useId();
  const [selection, setSelection] = useState<number | null>(null);
  if (history.length === 0) return <EmptyState title={tr("Seu histórico começa com um registro", "Your history starts with a record")} description={tr("Registre uma operação realizada para acompanhar o patrimônio a custo e os aportes líquidos ao longo do tempo.", "Record a completed transaction to track equity at cost and net contributions over time.")} />;
  const width = 900, height = 270, left = 84, right = 20, top = 22, bottom = 36;
  const values = history.flatMap(point => [Number(point.equity_at_cost), Number(point.net_contributions)]);
  if (values.some(value => !Number.isFinite(value))) return <EmptyState title={tr("Série indisponível", "Series unavailable")} description={tr("O histórico recebido contém valores indisponíveis.", "The supplied history contains unavailable values.")} />;
  const minimum = Math.min(0, ...values), maximum = Math.max(0, ...values);
  const span = maximum - minimum || 1;
  const start = new Date(history[0].date).getTime(), end = new Date(history[history.length - 1].date).getTime();
  const x = (index: number) => history.length === 1 ? (width + left - right) / 2 : left + ((new Date(history[index].date).getTime() - start) / (end - start || 1)) * (width - left - right);
  const y = (value: number) => top + (maximum - value) / span * (height - top - bottom);
  const cost = history.map((point, index) => `${x(index)},${y(Number(point.equity_at_cost))}`).join(" ");
  const contributions = history.map((point, index) => `${x(index)},${y(Number(point.net_contributions))}`).join(" ");
  const selected = Math.min(selection ?? history.length - 1, history.length - 1);
  const point = history[selected];
  const ticks = Array.from(new Set([0, Math.floor((history.length - 1) / 2), history.length - 1]));
  return <div className="history-chart"><div className="chart-legend"><span><i className="legend-line cyan" />{tr("Patrimônio a custo", "Equity at cost")}</span><span><i className="legend-line dashed" />{tr("Aportes líquidos", "Net contributions")}</span></div><div className="chart-current" aria-live="polite"><span>{date(point.date, language)}</span><strong>{money(point.equity_at_cost, language)}</strong><span className="muted">{tr("Aportes", "Contributions")} {money(point.net_contributions, language)}</span></div><div className="history-plot"><svg className="history-svg" viewBox={`0 0 ${width} ${height}`} role="img" aria-labelledby={`${id}-title ${id}-description`} onPointerMove={event => {
    const rect = event.currentTarget.getBoundingClientRect();
    const pointer = (event.clientX - rect.left) / rect.width * width;
    let closest = 0;
    history.forEach((_, index) => { if (Math.abs(x(index) - pointer) < Math.abs(x(closest) - pointer)) closest = index; });
    setSelection(closest);
  }}><title id={`${id}-title`}>{tr("Evolução do patrimônio a custo e dos aportes líquidos, em reais", "Equity at cost and net contributions over time, in BRL")}</title><desc id={`${id}-description`}>{tr("Não representa rentabilidade ou valor de mercado. Os valores exatos estão na tabela a seguir.", "This is not investment performance or market value. Exact values are available in the following table.")}</desc><defs><linearGradient id={`${id}-fill`} x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--chart-cost)" stopOpacity=".2" /><stop offset="100%" stopColor="var(--chart-cost)" stopOpacity="0" /></linearGradient></defs>{[0, .25, .5, .75, 1].map(fraction => { const value = minimum + span * fraction; const yy = y(value); return <g key={fraction}><line x1={left} x2={width - right} y1={yy} y2={yy} className="chart-grid" /><text x={left - 12} y={yy + 4} textAnchor="end" className="chart-label">{new Intl.NumberFormat(locale(language), { notation: "compact", maximumFractionDigits: 1 }).format(value)}</text></g>; })}<polygon points={`${x(0)},${y(minimum)} ${cost} ${x(history.length - 1)},${y(minimum)}`} fill={`url(#${id}-fill)`} /><polyline points={contributions} className="chart-line contributions-line" /><polyline points={cost} className="chart-line cost-line" />{history.length === 1 && <circle cx={x(0)} cy={y(Number(history[0].equity_at_cost))} r="4" fill="var(--chart-cost)" />}<line x1={x(selected)} x2={x(selected)} y1={top} y2={height - bottom} className="chart-crosshair" /><circle cx={x(selected)} cy={y(Number(point.equity_at_cost))} r="4" className="chart-point" />{ticks.map(index => <text key={index} x={x(index)} y={height - 10} textAnchor={index === 0 ? "start" : index === history.length - 1 ? "end" : "middle"} className="chart-label">{date(history[index].date, language)}</text>)}</svg></div><label className="chart-slider"><span className="muted small">{tr("Explorar data do histórico", "Explore a history date")}</span><input type="range" min={0} max={history.length - 1} value={selected} onChange={event => setSelection(Number(event.target.value))} aria-valuetext={`${date(point.date, language)}: ${money(point.equity_at_cost, language)}`} /></label><details className="chart-details"><summary>{tr("Ver valores em tabela", "View values in a table")}</summary><div className="table-scroll"><table><caption className="sr-only">{tr("Histórico a custo em BRL", "Cost history in BRL")}</caption><thead><tr><th>{tr("Data", "Date")}</th><th className="numeric">{tr("Patrimônio a custo", "Equity at cost")}</th><th className="numeric">{tr("Aportes líquidos", "Net contributions")}</th></tr></thead><tbody>{history.map(item => <tr key={item.date}><td>{date(item.date, language)}</td><td className="numeric">{money(item.equity_at_cost, language)}</td><td className="numeric">{money(item.net_contributions, language)}</td></tr>)}</tbody></table></div></details></div>;
}
