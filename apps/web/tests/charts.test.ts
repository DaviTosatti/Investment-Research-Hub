import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { AllocationChart } from "../src/components/allocation-chart";
import { HistoryChart } from "../src/components/history-chart";
import { LocaleProvider } from "../src/components/locale";
import type { Dashboard } from "../src/lib/types";

function allocationMarkup(allocation: Dashboard["allocation"], totalCost = "1000") {
  return renderToStaticMarkup(createElement(LocaleProvider, null,
    createElement(AllocationChart, { allocation, totalCost }),
  ));
}

test("allocation renders server weights directly and includes a labeled cost/weight table", () => {
  const markup = allocationMarkup([
    { asset_class: "stock", cost_basis: "250", weight: "25" },
    { asset_class: "etf", cost_basis: "750", weight: "75" },
  ]);
  assert.match(markup, /stroke-dasharray="25 75"/);
  assert.match(markup, /stroke-dasharray="75 25"/);
  assert.match(markup, /stroke-dashoffset="-25"/);
  assert.match(markup, /role="img" aria-labelledby=/);
  assert.match(markup, /<caption[^>]*>Legenda da alocação/);
  assert.match(markup, /<th scope="row"><span aria-hidden="true" class="allocation-dot allocation-stock"/);
  assert.match(markup, /Ações/);
  assert.match(markup, /<title>Ações: 25%<\/title>/);
  assert.match(markup, /R\$\s*250,00/);
  assert.match(markup, /25%/);
  assert.match(markup, /Caixa por negociação fora desta distribuição/);
});

test("allocation neither renormalizes supplied weights nor changes class colors with filters", () => {
  const markup = allocationMarkup([
    { asset_class: "fii", cost_basis: "200", weight: "20" },
    { asset_class: "etf", cost_basis: "300", weight: "30" },
  ]);
  assert.match(markup, /stroke-dasharray="20 80"/);
  assert.match(markup, /stroke-dasharray="30 70"/);
  assert.match(markup, /donut-segment allocation-etf/);
  const filtered = allocationMarkup([{ asset_class: "etf", cost_basis: "300", weight: "100" }], "300");
  assert.match(filtered, /donut-segment allocation-etf/);
  assert.match(filtered, /stroke-dasharray="100 0"/);
  assert.match(filtered, /R\$\s*300,00/);
});

test("missing allocation shows an empty state and invalid geometry retains its source table", () => {
  const empty = allocationMarkup([], "0");
  assert.match(empty, /Alocação ainda indisponível/);
  assert.doesNotMatch(empty, /<svg[^>]*class="allocation-donut"/);
  const invalid = allocationMarkup([{ asset_class: "stock", cost_basis: "50", weight: "101" }], "50");
  assert.match(invalid, /Gráfico indisponível/);
  assert.match(invalid, /101%/);
  assert.match(invalid, /R\$\s*50,00/);
  assert.doesNotMatch(invalid, /stroke-dasharray/);
});

test("cost history keeps the exact API figures in an accessible table and preserves its performance limitation", () => {
  const markup = renderToStaticMarkup(createElement(LocaleProvider, null,
    createElement(HistoryChart, { history: [{ date: "2026-11-04", equity_at_cost: "9007199254740993.12", net_contributions: "1000" }] }),
  ));
  assert.match(markup, /class="history-plot"/);
  assert.match(markup, /class="cost-line|class="chart-line cost-line"/);
  assert.match(markup, /Não representa rentabilidade ou valor de mercado/);
  assert.match(markup, /04\/11\/2026/);
  assert.match(markup, /9\.007\.199\.254\.740\.993,12/);
  assert.match(markup, /<caption[^>]*>Histórico a custo em BRL/);
});
