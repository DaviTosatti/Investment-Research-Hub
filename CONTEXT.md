# Contexto da Raiz — Investment Research Hub

## 1. Missão e Objetivo (Goal)
O **Investment Research Hub** é uma plataforma privada e colaborativa em desenvolvimento para pesquisa, aprendizado e acompanhamento contábil-financeiro de investimentos em ativos brasileiros e globais (ações, FIIs, renda fixa, ETFs).
O objetivo do repositório raiz é orquestrar o monólito modular, unificando os contratos de ambiente de desenvolvimento (Windows nativo e Linux/Docker), dependências Python (`uv`) e Web (`npm`), além de orientar agentes de IA e humanos pelo mapa de contexto ICM (Layer 0 e Layer 1).

Esta revisão dos 11 contextos descreve a base `5aaf5d8`, anterior à integração das novas capacidades de importação. Usa a [comparação detalhada](docs/CONTEXT_PLAN_COMPARISON.md) e os fontes citados em cada área. A Etapa 1 permanece em implementação; nenhuma etapa ou skill completa é declarada validada por esta revisão.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Governança Global e Documentos Mestres:**
  - `AGENTS.md`: Identidade Layer 0, regras invariantes, roteamento de contexto ICM.
  - `CLAUDE.md`: Apontador unificado para `@AGENTS.md`.
  - `CONTRIBUTING.md`: Padrão de Conventional Commits (`feat`, `fix`, `docs`, etc.).
  - `README.md` e `LEIA-ME-WINDOWS.txt`: Guias operacionais e de inicialização.
  - `skills-lock.json`: Registro SHA-256 das skills de desenvolvimento; o check da base falha por hashes divergentes, conforme a auditoria F09.
- [x] **Configurações de Tooling e Runtime:**
  - `pyproject.toml` + `uv.lock`: Python >=3.12,<3.14 (CI em 3.12), gerenciado por `uv`; Ruff (line-length 100), Mypy restrito a `hub_finance` e Pytest com Hypothesis.
  - `alembic.ini`: Configuração de migrações relacionais para PostgreSQL.
  - `compose.yaml`: PostgreSQL 17.6 em container para desenvolvimento Linux/macOS.
  - `.env.example`: Modelo de configuração local; credenciais reais permanecem fora do Git.
- [x] **Scripts de Inicialização e Porte Windows Nativo:**
  - `Iniciar Hub.cmd`, `Parar Hub.cmd`, `Verificar Hub.cmd`: Atalhos operacionais de duplo clique para Windows.
- [x] **Árvores de Diretórios com Contexto:**
  - `apps/`: Processos e servidores da aplicação (`api`, `web`).
  - `packages/`: Pacotes de domínio reutilizáveis (`engines`).
  - `tests/`: Bateria de testes unitários, integração e Windows nativo.
  - `scripts/`: Runtimes, bootstraps e sincronizador de skills.
  - `docs/`: Especificação, plano de 3 etapas, status e arquitetura.
  - `.agents/`: Skills de engenharia multi-LLM (Antigravity/Codex) e `.claude/` (espelho Claude Code).
  - `.github/`: Workflows de CI (`verify.yml`, `windows.yml`).

Fontes do inventário: [manifesto Python](pyproject.toml), [manifesto web](apps/web/package.json), [Compose](compose.yaml) e [auditoria F09/F11](docs/CONTEXT_PLAN_COMPARISON.md). A existência de workflows não comprova proteção obrigatória de branch nem aprovação de toda a API pelo Mypy.

## 3. Regras de Negócio e Invariantes Globais (Layer 0)
- **Monólito Modular:** Frontend (`web`) e Backend (`api`) são processos separados. O ledger Python (`hub_finance`) é reutilizado pela API; avaliações e agregações ainda residem em [portfolio_service.py](apps/api/src/hub_api/portfolio_service.py). Futuros workers, MCP e exportadores devem reutilizar esses cálculos canônicos, sem fórmulas paralelas no frontend.
- **Precisão Financeira Estrita:** Valores monetários são manipulados obrigatoriamente como `Decimal` (ou string em trânsito JSON); `float` é terminantemente proibido para dinheiro.
- **Titularidade e Autoria:** Preservar titular econômico e autor sem confundir titular com usuário de acesso. Nos [modelos atuais](apps/api/src/hub_api/models.py), `Transaction` tem `owner_id` e `created_by`; contas/carteiras têm vínculo ao titular, `Price` tem autor, e vários cadastros têm autoria em `AuditEvent.actor_id`. Esses campos não existem em toda entidade. O grupo compartilha consultas; escrita é controlada por papel em [security.py](apps/api/src/hub_api/security.py), sem ACL usuário–titular.
- **Natureza dos Eventos:** Operações registradas são **fatos econômicos já realizados**, nunca ordens enviadas a corretoras.
- **Segredos e Caches:** Nunca versionar arquivos `.env`, extratos, carteiras pessoais, dumps SQL, caches (`.pytest_cache`, `.next`, `__pycache__`) ou credenciais.
- **Preservação de Escopo:** O plano de 3 etapas e as 23 skills de negócio de `docs/REQUIREMENTS_MATRIX.md` são inegociáveis. Não simular conclusão através de documentação estática ou mocks.

## 4. Mapa de Roteamento de Contexto (ICM Layer 1)

| Pedido ou Domínio de Trabalho | Contexto Responsável |
| :--- | :--- |
| API REST `/api/v1`, autenticação, PostgreSQL, ORM, schemas | [apps/api/CONTEXT.md](apps/api/CONTEXT.md) |
| Interface Web Next.js, páginas financeiras, CSS próprio, gráficos | [apps/web/CONTEXT.md](apps/web/CONTEXT.md) |
| Motor contábil `hub_finance`, ledger de eventos, cálculo de saldos | [packages/engines/CONTEXT.md](packages/engines/CONTEXT.md) |
| Testes unitários, de integração, propriedades Hypothesis e testes Windows | [tests/CONTEXT.md](tests/CONTEXT.md) |
| Automações, download de runtimes Windows, script de sync de skills | [scripts/CONTEXT.md](scripts/CONTEXT.md) |
| Planos, matriz de requisitos, decisões de arquitetura e baseline | [docs/CONTEXT.md](docs/CONTEXT.md) |
| Skills de desenvolvimento, checklists de engenharia, agentes | [.agents/CONTEXT.md](.agents/CONTEXT.md) |
| Pipelines de CI/CD GitHub Actions, templates de PR | [.github/CONTEXT.md](.github/CONTEXT.md) |

## 5. Roteiro por Etapas (Ao fim das etapas)

Compromissos do [plano](docs/IMPLEMENTATION_PLAN.md) e da [matriz](docs/REQUIREMENTS_MATRIX.md); os itens abaixo continuam pendentes até evidência de integração.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Instalação limpa no Windows e Linux documentada e reproduzível sem dependências ocultas.
  - Procedimento de backup consistente e restauração em destino vazio demonstrado e testado para banco, originais, snapshots, artefatos e configuração da cobertura entregue, com credenciais separadas.
  - CI verde e obrigatório para API, Frontend e Porte Windows.
  - 12 páginas-base do Hub integradas a dados reais com 2 usuários autorizados simultâneos e titulares distintos.
  - S01 (Carteiras), S02 (Mercado), S12 (Auditoria), S03 (Fundamentos), S07 (Macro), S21 (Relatórios), S23 (Aprendizado) com contratos, fontes, serviços/motores, telas, procedimentos, ferramentas/wrappers e avaliações executadas; diário/teses/comentários básicos, metas e performance incluídos na cobertura da etapa.
  - Identidade emissor/instrumento/listagem, fontes reais verificadas, originais preservados, disponibilidade histórica, revisões e snapshots recuperáveis; CSV/XLSX com mapeamento, prévia, confirmação, reconciliação, quarentena e correção rastreável.
  - Jobs duráveis antes de aceitar trabalho em segundo plano, com estados persistidos, retomada, cancelamento explícito e efeitos financeiros atômicos; MCP inicial e relatórios coerentes com tela/snapshot.
  - Manifesto dos motores e primeira linha de base efetivamente medida; jornada A e recortes B/F, reinício com dados/preferências preservados e revisão visual em 1440/1024/768/390 px.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Introdução de módulos aceleradores (Rust/Julia) somente se houver ganho de desempenho e equivalência numérica medidos.
  - Lockfiles e migrações preservados sem quebrar a camada Python de referência.
  - 12 skills avançadas (S19, S10, S09, S15, S04, S16, S05, S17, S06, S14, S08, S11) e páginas P05–P07, P09, P13–P17 integradas.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Restauração de desastre testada a partir de ambiente completamente zerado.
  - 23 skills de negócio operando de forma integrada nas 23 páginas do Hub.
  - Comitê de IA (S22) com auditoria de evidências e críticas com decisão humana separada.

## 6. O Que Fica Fora de Escopo
- Não criar módulos vazios, pastas sem código ou mocks estáticos para simular etapas futuras.
- Não introduzir dependências ou microserviços externos sem necessidade comprovada.
- Não transformar o Hub em um sistema de ordens ou home-broker conectado a corretoras.

## 7. Verificação e Comandos
- **Sincronização de skills:** `python scripts/sync_agent_skills.py --check` (somente leitura; falha conhecida na base, não equivale a check aprovado).
- **Verificação geral Windows:** Executar `Verificar Hub.cmd`
- **Verificação Linux/CI:** `bash scripts/check.sh` (com dependências e PostgreSQL preparados; inclui testes/build web e Mypy do motor, não de toda a API).
