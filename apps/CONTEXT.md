# Contexto de `apps/`

**Escopo:** processos executáveis do monólito modular. Cada app tem contexto próprio; cálculos não ficam aqui, e sim em [packages/engines](../packages/engines/CONTEXT.md).

## O que existe hoje

- [x] [`api/`](api/CONTEXT.md) — FastAPI, SQLAlchemy, Alembic, PostgreSQL
- [x] [`web/`](web/CONTEXT.md) — Next.js (App Router), TypeScript

## Padrões

- Frontend, API, MCP e exportações compartilham o mesmo motor Python; nenhum app reimplementa cálculo.
- Contratos HTTP em `/api/v1` descritos em [docs/API_CONTRACT.md](../docs/API_CONTRACT.md).

## Ao fim das etapas

- [ ] **Etapa 1:** `api` + `web` cobrem as 12 páginas-base; MCP inicial e jobs persistidos.
- [ ] **Etapa 2:** páginas P05–P07, P09, P13–P17 ampliam bases existentes.
- [ ] **Etapa 3:** processo worker próprio (só quando implementado) e 23 páginas integradas às 23 skills.

## Fora de escopo

Pastas novas (`worker`, `mcp`) só nascem com código e testes reais.
