# Contexto de `.github/`

**Escopo:** CI e template de PR.

## O que existe hoje

- [x] `workflows/verify.yml`: jobs `api` (PostgreSQL, migrações, testes) e `web` (install, typecheck, lint, test, build)
- [x] `workflows/windows.yml`: instalação limpa, testes e ZIP do porte Windows
- [x] `pull_request_template.md`

## Padrões

Conventional Commits ([CONTRIBUTING.md](../CONTRIBUTING.md)); push por incremento verificado, sem force push.

## Ao fim das etapas

- [ ] **Etapa 1:** passo `python scripts/sync_agent_skills.py --check` no `verify.yml`.
- [ ] **Etapa 3:** pipeline de release e atualização.
