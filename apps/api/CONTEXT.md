# Contexto de `apps/api`

**Escopo:** API HTTP `/api/v1`, autenticação, persistência e orquestração. Regras financeiras vêm de `hub_finance`.

## O que existe hoje

- [x] `src/hub_api/`: `main.py` (rotas), `models.py`, `schemas.py`, `portfolio_service.py`, `security.py`, `config.py`, `errors.py`, `responses.py`, `cli.py`, `windows_runtime.py`
- [x] Rotas: `health`, `openapi.json`, `auth` (login/session/logout), `members`, `owners`, `portfolios`, `instruments`, `prices`, `transactions`, `dashboard`, `reports/positions.csv`, `audit`
- [x] `migrations/`: Alembic (`fde27e01f059` fundação, `0002` integridade do ledger)

## Padrões

- Titularidade econômica e autoria explícitas em toda escrita; eventos imutáveis, correções por novo evento.
- Valores monetários como `Decimal`/string; nunca `float`.
- Operações são fatos realizados, nunca ordens a corretoras.
- Toda mudança de `models.py` traz migração Alembic e teste de integração PostgreSQL.
- Erros via `errors.py`; respostas paginadas via `responses.py`.

## Ao fim das etapas

- [ ] **Etapa 1:** endpoints das 7 skills (S01, S02, S03, S07, S12, S21, S23), MCP inicial, jobs persistidos, backup/restauração, duas contas autorizadas.
- [ ] **Etapa 2:** serviços dos 12 motores avançados com versão e explicação.
- [ ] **Etapa 3:** eventos oficiais, comitê IA (snapshot, crítica, decisão humana), alertas, agendamentos, catch-up.
- [ ] `portfolio_service.py` dividido por domínio quando crescer (sem duplicar cálculo).

## Fora de escopo

Cálculo financeiro (→ engines), apresentação (→ web).

## Verificação

`pytest tests/integration` (PostgreSQL), `ruff`, `mypy`, `alembic check`. Ver [tests/CONTEXT.md](../../tests/CONTEXT.md).
