# Contexto da raiz

**Escopo:** entradas de execução, configuração e roteamento. Regras globais estão em [AGENTS.md](AGENTS.md); este arquivo mostra o que existe na raiz e o que ela deve ter ao fim de cada etapa. Metodologia: [docs/metodologia-contexto.md](docs/metodologia-contexto.md).

## O que existe hoje

- [x] `AGENTS.md` (regras), `CLAUDE.md` (aponta para AGENTS.md), `CONTRIBUTING.md`, `README.md`
- [x] `pyproject.toml` + `uv.lock` (Python, ruff line-length 100, mypy, pytest), `alembic.ini`, `compose.yaml`, `.env.example`
- [x] Iniciadores Windows: `Iniciar Hub.cmd`, `Parar Hub.cmd`, `Verificar Hub.cmd`, `LEIA-ME-WINDOWS.txt`
- [x] `skills-lock.json` (hash das skills de desenvolvimento, gerado por `scripts/sync_agent_skills.py`)
- [x] Pastas: `apps/`, `packages/`, `tests/`, `scripts/`, `docs/`, `.agents/`, `.github/`

## Padrões

- Segredos, extratos, carteiras pessoais, backups e caches nunca entram no Git (`.gitignore`).
- Cada pasta relevante tem `CONTEXT.md` com: o que existe, padrões, pendências por etapa, fora de escopo e verificação. Atualize-o no mesmo commit que muda a pasta.
- Uma regra vale na pasta mais baixa que a governa; sobe de nível só se valer para várias subpastas.

## Roteamento

| Pedido | Contexto |
| --- | --- |
| API, banco, autenticação | [apps/api/CONTEXT.md](apps/api/CONTEXT.md) |
| Interface Next.js | [apps/web/CONTEXT.md](apps/web/CONTEXT.md) |
| Motor financeiro (Decimal, ledger) | [packages/engines/CONTEXT.md](packages/engines/CONTEXT.md) |
| Testes | [tests/CONTEXT.md](tests/CONTEXT.md) |
| Scripts e Windows | [scripts/CONTEXT.md](scripts/CONTEXT.md) |
| Documentação, plano, status | [docs/CONTEXT.md](docs/CONTEXT.md) |
| Skills e agentes de desenvolvimento | [.agents/CONTEXT.md](.agents/CONTEXT.md) |
| CI e PR | [.github/CONTEXT.md](.github/CONTEXT.md) |

## Ao fim das etapas (checklist da raiz)

- [ ] **Etapa 1:** instalação limpa e atualização documentadas; backup/restauração demonstráveis; CI verde (api, web, windows).
- [ ] **Etapa 2:** manifesto dos motores aceleráveis (Rust/Julia) somente se benefício medido; lockfiles preservados.
- [ ] **Etapa 3:** instalação alvo e atualização revisadas; restauração em ambiente vazio testada.
- [ ] Nenhuma pasta vazia criada só para demonstrar arquitetura.

## Fora de escopo

Regras detalhadas de domínio, API ou UI: ficam no `CONTEXT.md` da pasta responsável.
