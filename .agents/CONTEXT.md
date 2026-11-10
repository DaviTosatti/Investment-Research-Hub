# Contexto de `.agents/`

**Escopo:** skills e papéis de **desenvolvimento**, para qualquer LLM. Não são as 23 skills de negócio do Hub.

## O que existe hoje

- [x] `skills/` — fonte canônica (Antigravity e Codex leem `.agents/skills`): 25 skills de [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) + `reverse-engineer-anything` de [morluto/rea](https://github.com/morluto/rea)
- [x] `references/` — checklists citados pelas skills (`../../references/`)
- [x] `development/README.md` — papéis do projeto (integração, interface, documentação, revisão financeira)
- [x] Espelho para Claude Code em `.claude/skills` e `.claude/references` (gerado)

## Padrões

- **Edite só `.agents/`.** Depois rode `python scripts/sync_agent_skills.py` (gera `.claude/` e `skills-lock.json`); CI usa `--check`.
- Skill local do Hub = pasta nova com `SKILL.md`; registre a origem em `scripts/sync_agent_skills.py`.
- Skills externas não são editadas; atualize copiando da origem e rodando o sync.
- REA só para engenharia reversa de artefatos entregues, não para analisar este código.

## Ao fim das etapas

- [ ] **Etapa 1:** procedimentos/avaliações das 7 skills de negócio documentados.
- [ ] **Etapa 2:** idem para as 12 skills avançadas.
- [ ] **Etapa 3:** 23 skills com wrappers equivalentes; verificação `--check` no CI.
