# Contexto de `scripts/`

**Escopo:** automação de ambiente, verificação e porte Windows.

## O que existe hoje

- [x] `bootstrap.sh`, `check.sh` (Linux/CI)
- [x] `windows/`: `Start-Hub.ps1`, `runtime.py`, `downloads.json` (runtimes portáteis com hashes)
- [x] `sync_agent_skills.py`: espelha `.agents/skills` → `.claude/skills` e atualiza `skills-lock.json` (`--check` no CI)

## Padrões

- Scripts idempotentes, sem segredos; downloads com SHA-256 fixo.
- Caminhos com acentos/espaços suportados no Windows.

## Ao fim das etapas

- [ ] **Etapa 1:** backup/restauração e atualização por script.
- [ ] **Etapa 3:** instalação limpa e atualização alvo documentadas; restauração em ambiente vazio.
