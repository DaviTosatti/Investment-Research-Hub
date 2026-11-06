"use client";

import { useId } from "react";
import type { Dashboard } from "@/lib/types";
import { classLabels, label, money, percent } from "@/lib/format";
import { useLocale } from "./locale";
import { EmptyState, Icon } from "./ui";

const classColors: Record<string, string> = {
  stock: "allocation-stock", fii: "allocation-fii", etf: "allocation-etf",
  fixed_income: "allocation-fixed-income", other: "allocation-other",
};

export function AllocationChart({ allocation, totalCost }: { allocation: Dashboard["allocation"]; totalCost: string }) {
  const { language, tr } = useLocale();
  const id = useId();
  if (allocation.length === 0) return <EmptyState icon="wallet" title={tr("Alocação ainda indisponível", "No allocation yet")} description={tr("As classes aparecem quando houver posições registradas.", "Asset classes appear once positions have been recorded.")} />;

  // These offsets are SVG geometry only. Never derive or normalize the engine's weights.
  const segments = allocation.map((item, index) => {
    const weight = Number(item.weight);
    const offset = allocation.slice(0, index).reduce((sum, entry) => sum + Number(entry.weight), 0);
    return { ...item, displayWeight: item.weight, weight, offset, color: classColors[item.asset_class] ?? "allocation-other" };
  });
  const validGeometry = segments.every(item => Number.isFinite(item.weight) && item.weight >= 0 && item.weight <= 100);

  return <div className="allocation-chart">
    {validGeometry ? <figure className="allocation-figure">
      <svg className="allocation-donut" viewBox="0 0 220 220" role="img" aria-labelledby={`${id}-title ${id}-description`}>
        <title id={`${id}-title`}>{tr("Alocação por classe sobre o custo das posições", "Asset allocation based on position cost")}</title>
        <desc id={`${id}-description`}>{tr("Pesos recebidos do motor, sem incluir caixa. A legenda e os valores estão na tabela abaixo.", "Engine-supplied weights, excluding cash. Labels and values are in the table below.")}</desc>
        <circle className="donut-track" cx="110" cy="110" r="88" />
        <g transform="rotate(-90 110 110)">{segments.map(item => <circle key={item.asset_class} className={`donut-segment ${item.color}`} cx="110" cy="110" r="88" pathLength="100" strokeDasharray={`${item.weight} ${100 - item.weight}`} strokeDashoffset={-item.offset}>
          <title>{`${label(classLabels, item.asset_class, language)}: ${percent(item.displayWeight, language)}`}</title>
        </circle>)}</g>
      </svg>
      <figcaption className="donut-center"><span>{tr("BASE DE CUSTO", "COST BASIS")}</span><strong>{money(totalCost, language)}</strong><small>BRL</small></figcaption>
    </figure> : <p className="allocation-unavailable" role="status">{tr("Gráfico indisponível: confira os pesos informados na tabela.", "Chart unavailable: check the supplied weights in the table.")}</p>}
    <div className="allocation-legend-scroll"><table className="allocation-table"><caption className="sr-only">{tr("Legenda da alocação: classe, custo em BRL e peso calculado pelo motor", "Allocation legend: asset class, cost in BRL and engine-calculated weight")}</caption>
      <thead><tr><th scope="col">{tr("Classe", "Class")}</th><th scope="col" className="numeric">{tr("Custo", "Cost")}</th><th scope="col" className="numeric">%</th></tr></thead>
      <tbody>{allocation.map(item => <tr key={item.asset_class}><th scope="row"><span aria-hidden="true" className={`allocation-dot ${classColors[item.asset_class] ?? "allocation-other"}`} />{label(classLabels, item.asset_class, language)}</th><td className="numeric">{money(item.cost_basis, language)}</td><td className="numeric">{percent(item.weight, language)}</td></tr>)}</tbody>
    </table></div>
    <p className="allocation-note"><Icon name="shield" size={14} />{tr("Pesos calculados pelo motor. Caixa por negociação fora desta distribuição.", "Weights calculated by the engine. Trade-date cash excluded from this distribution.")}</p>
  </div>;
}
