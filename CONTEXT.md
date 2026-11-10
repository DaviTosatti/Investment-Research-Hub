# Contexto da Raiz — Investment Research Hub

## 1. Missão e Objetivo (Goal)
O **Investment Research Hub** é uma plataforma institucional de inteligência, análise fundamentalista e acompanhamento contábil-financeiro de investimentos em ativos brasileiros e globais (ações, FIIs, renda fixa, ETFs).
O objetivo do repositório raiz é orquestrar o monólito modular, unificando os contratos de ambiente de desenvolvimento (Windows nativo e Linux/Docker), dependências Python (`uv`) e Web (`npm`), além de orientar agentes de IA e humanos pelo mapa de contexto ICM (Layer 0 e Layer 1).

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Governança Global e Documentos Mestres:**
  - `AGENTS.md`: Identidade Layer 0, regras invariantes, roteamento de contexto ICM.
  - `CLAUDE.md`: Apontador unificado para `@AGENTS.md`.
  - `CONTRIBUTING.md`: Padrão de Conventional Commits (`feat`, `fix`, `docs`, etc.).
  - `README.md` e `LEIA-ME-WINDOWS.txt`: Guias operacionais e de inicialização.
  - `skills-lock.json`: Lockfile de integridade criptográfica SHA-256 das skills de desenvolvimento multi-LLM.
- [x] **Configurações de Tooling e Runtime:**
  - `pyproject.toml` + `uv.lock`: Configuração Python 3.12 gerenciada por `uv`, linters Ruff (line-length 100), Mypy e Pytest com Hypothesis.
  - `alembic.ini`: Configuração de migrações relacionais para PostgreSQL.
  - `compose.yaml`: PostgreSQL 17.6 em container para desenvolvimento Linux/macOS.
  - `.env.example`: Modelo de variáveis de ambiente obrigatórias sem expor segredos.
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

## 3. Regras de Negócio e Invariantes Globais (Layer 0)
- **Monólito Modular:** Frontend (`web`), Backend (`api`) e futuros Workers executam em processos isolados, mas compartilham estritamente os contratos e o mesmo motor numérico Python (`hub_finance`).
- **Precisão Financeira Estrita:** Valores monetários são manipulados obrigatoriamente como `Decimal` (ou string em trânsito JSON); `float` é terminantemente proibido para dinheiro.
- **Titularidade e Autoria:** Todas as operações financeiras e cadastros registram titular econômico (`owner_id`) e autor da inserção (`created_by`).
- **Natureza dos Eventos:** Operações registradas são **fatos econômicos já realizados**, nunca ordens enviadas a corretoras.
- **Segredos e Caches:** Nunca versionar arquivos `.env`, extratos, carteiras pessoais, dumps SQL, caches (`.pytest_cache`, `.next`, `__pycache__`) ou credenciais.
- **Preservação de Escopo:** O plano de 3 etapas e as 23 skills de negócio de `docs/REQUIREMENTS_MATRIX.md` são inegociáveis. Não simular conclusão através de documentação estática ou mocks.

## 4. Mapa de Roteamento de Contexto (ICM Layer 1)

| Pedido ou Domínio de Trabalho | Contexto Responsável |
| :--- | :--- |
| API REST `/api/v1`, autenticação, PostgreSQL, ORM, schemas | [apps/api/CONTEXT.md](apps/api/CONTEXT.md) |
| Interface Web Next.js, páginas financeiras, Tailwind, gráficos | [apps/web/CONTEXT.md](apps/web/CONTEXT.md) |
| Motor contábil `hub_finance`, ledger de eventos, cálculo de saldos | [packages/engines/CONTEXT.md](packages/engines/CONTEXT.md) |
| Testes unitários, de integração, propriedades Hypothesis e testes Windows | [tests/CONTEXT.md](tests/CONTEXT.md) |
| Automações, download de runtimes Windows, script de sync de skills | [scripts/CONTEXT.md](scripts/CONTEXT.md) |
| Planos, matriz de requisitos, decisões de arquitetura e baseline | [docs/CONTEXT.md](docs/CONTEXT.md) |
| Skills de desenvolvimento, checklists de engenharia, agentes | [.agents/CONTEXT.md](.agents/CONTEXT.md) |
| Pipelines de CI/CD GitHub Actions, templates de PR | [.github/CONTEXT.md](.github/CONTEXT.md) |

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Instalação limpa no Windows e Linux documentada e reproduzível sem dependências ocultas.
  - Procedimento de backup e restauração de dados demonstrado e testado.
  - CI verde e obrigatório para API, Frontend e Porte Windows.
  - 12 páginas-base do Hub integradas a dados reais com 2 usuários autorizados simultâneos e titulares distintos.
  - S01 (Carteiras), S02 (Mercado), S12 (Auditoria), S03 (Fundamentos), S07 (Macro), S21 (Relatórios), S23 (Aprendizado) com bases funcionais.
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
- **Sincronização de skills:** `python scripts/sync_agent_skills.py --check`
- **Verificação geral Windows:** Executar `Verificar Hub.cmd`
- **Verificação Linux/CI:** `bash scripts/check.sh`
