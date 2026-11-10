# Contexto de `packages/engines`

**Escopo:** motor financeiro Python (`hub_finance`), única fonte de cálculo para API, MCP, UI e relatórios.

## O que existe hoje

- [x] `src/hub_finance/ledger.py`: eventos `Decimal`, lançamentos balanceados, posições, caixa, custo
- [x] `py.typed`, tipagem verificada por mypy

## Padrões

- `Decimal` com política de arredondamento explícita; sem `float`, sem I/O, sem dependência de web/API.
- Funções puras e determinísticas; invariantes cobertas por Hypothesis.
- Contratos separam método financeiro, implementação e configuração de execução.

## Ao fim das etapas

- [ ] **Etapa 1:** splits, câmbio, proventos, transferências, custo/resultado, TWR/MWR (ou aproximação nomeada), conciliação independente (T01–T07, T15, T21, T25–T26).
- [ ] **Etapa 2:** renda fixa, FIIs, ETFs, valuation, tributação com vigências, risco, Monte Carlo único, otimização, sinais, backtest sem look-ahead, radar.
- [ ] **Etapa 3:** reconciliação de eventos oficiais, detecção de anomalias.
- [ ] Linha de base de desempenho em [docs/PERFORMANCE_BASELINE.md](../../docs/PERFORMANCE_BASELINE.md).

## Fora de escopo

Persistência, HTTP, apresentação.

## Verificação

`pytest tests/unit`, `mypy`, `ruff`.
