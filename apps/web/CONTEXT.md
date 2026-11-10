# Contexto de `apps/web`

**Escopo:** interface Next.js/TypeScript na identidade fintech escura do Hub. Consome somente a API; não calcula regra financeira.

## O que existe hoje

- [x] `src/app/(hub)/`: `inicio`, `carteiras`, `operacoes`, `dados`, `administracao`; `login`, `error`, `not-found`
- [x] `src/components/`: shell, tabelas, gráficos (alocação/histórico), formulário de preço manual, exportação CSV, `ui.tsx`
- [x] `src/lib/`: `api.ts`, `format.ts`, `forms.ts`, `types.ts`, `use-resource.ts`
- [x] `tests/` (Vitest-style): api, charts, format, forms — 24 testes

## Padrões

- Valores monetários exibidos a partir de strings Decimal da API; sem aritmética em `number`.
- Datas/fuso tratados em `format.ts`; formulários idempotentes (`forms.ts`).
- Componentes seguem [docs/VISUAL_REFERENCES.md](../../docs/VISUAL_REFERENCES.md), conforme a etapa de cada tela.
- Acessibilidade e responsividade desktop/celular desde a etapa 1.

## Ao fim das etapas

- [ ] **Etapa 1:** 12 páginas-base (P01–P04, P08, P10–P12, P19, P21–P23) com dados reais, estados de erro/vazio e QA visual.
- [ ] **Etapa 2:** P05–P07, P09, P13–P17 (valuation, risco, simulação, backtest, radar).
- [ ] **Etapa 3:** agenda, alertas, comitê, colaboração; 23 páginas ↔ 23 skills.
- [ ] Revisão desktop/celular e metas de desempenho medidas.

## Fora de escopo

Mocks que simulem módulos integrados; lógica de negócio.

## Verificação

`npm run typecheck`, `lint`, `test`, `build` em `apps/web`.
