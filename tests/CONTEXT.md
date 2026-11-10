# Contexto de `tests/`

**Escopo:** testes Python. Testes web ficam em `apps/web/tests`.

## O que existe hoje

- [x] `unit/`: `test_ledger`, `test_ledger_adversarial`, `test_windows_runtime`
- [x] `integration/` (PostgreSQL): `test_contracts`, `test_native_admin`, `test_portfolios`, `test_review_regressions`, `conftest.py`
- [x] `windows/verify_native.py`: verificação ponta a ponta do porte Windows (122 testes Python no CI)

## Padrões

- Todo bug corrigido ganha teste de regressão; casos adversariais (concorrência, falta de caixa, isolamento por titular).
- Casos normativos T01–T56 da matriz só viram "validado" com teste executado.
- Não declarar testes não executados.

## Ao fim das etapas

- [ ] **Etapa 1:** casos T01–T07, T15, T21, T25–T26; avaliações das 7 skills; duas contas.
- [ ] **Etapa 2:** backtest conhecido, tributação por vigência, equivalência de motores acelerados.
- [ ] **Etapa 3:** restauração em ambiente vazio, catch-up, cancelamento/retomada, evento→alerta sem duplicação.
