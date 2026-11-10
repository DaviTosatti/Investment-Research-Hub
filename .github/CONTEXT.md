# Contexto de `.github/` — Integração Contínua (CI), Automações e Pull Requests

## 1. Missão e Objetivo (Goal)
O diretório `.github/` abriga os fluxos de trabalho de Integração Contínua (CI), automações de checagem de qualidade e templates de Pull Request do repositório no GitHub.
Sua missão é atuar como o **gatekeeper inegociável da qualidade de código**, garantindo que nenhum incremento seja integrado à branch de trabalho ou à produção sem antes passar por uma suíte completa de checagem estática (linters e checagem de tipos), testes de unidade e integração (PostgreSQL real), compilação do frontend Next.js e validação da distribuição nativa em ambiente Windows.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Workflows do GitHub Actions (`workflows/`):**
  - `verify.yml`: Workflow multiplataforma principal contendo dois jobs paralelos:
    - `api`: Inicializa serviço PostgreSQL 17, instala Python 3.12 com `uv`, aplica migrações Alembic, roda linters (Ruff), checagem de tipos (Mypy) e executa a suíte de testes completa (`tests/unit` e `tests/integration`).
    - `web`: Instala dependências com `npm ci`, roda checagem de tipos TypeScript (`npm run typecheck`), linter (`npm run lint`), testes unitários (`npm run test`) e build de produção (`npm run build`).
  - `windows.yml`: Workflow dedicado ao porte Windows Server 2022 x64 que valida a instalação limpa, downloads de runtimes com validação de hashes SHA-256, execução de caminhos com acentos/espaços e empacotamento do ZIP de release.
- [x] **Templates de Governança (`pull_request_template.md`):**
  - Modelo padronizado de descrição de PRs exigindo declaração de: etapa do plano, skills afetadas, comandos reais executados, evidências de testes e confirmação de não-inclusão de dados sensíveis ou carteiras pessoais.

## 3. Regras de Negócio e Invariantes do CI
- **Proibição Estrita de Force Push:** É expressamente vedado o uso de `git push --force` ou reescrita de histórico já publicado no repositório remoto.
- **Padrão Conventional Commits:** Todas as mensagens de commit e títulos de PRs devem seguir a convenção formal:
  - `feat(<escopo>): ...` — Novas funcionalidades.
  - `fix(<escopo>): ...` — Correções de bugs.
  - `docs(<escopo>): ...` — Documentação e contextos ICM.
  - `test(<escopo>): ...` — Adição ou ajuste de testes.
  - `chore(<escopo>): ...` — Ajustes de dependências e tooling.
  - `ci(<escopo>): ...` — Alterações em pipelines do GitHub Actions.
- **Proibição de Bypass de Quality Gates:** PRs com falha em qualquer job do CI (`api`, `web` ou `windows`) não devem ser mesclados.
- **Proteção de Segredos:** O CI nunca deve expor credenciais em logs públicos. Todas as credenciais de teste são geradas em memória e efêmeras.

## 4. Contratos de Execução dos Workflows
- **Trigger:** Os workflows disparam automaticamente em `push` e `pull_request` mirando as branches principais (`main`, `codex/*`).
- **PostgreSQL em CI:** O job `api` obrigatoriamente provisiona um container oficial de PostgreSQL com as credenciais padrão de teste, garantindo paridade com os testes locais.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Adição de step no workflow `verify.yml` para rodar `python scripts/sync_agent_skills.py --check`, garantindo que o lockfile e o espelho das skills de IA nunca cheguem desatualizados ao repositório.
  - Adição de checagem automática de links quebrados nos arquivos de documentação (`docs/`).
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Inclusão de testes de performance e checagem de regressão contra a linha de base de tempo registrada em `docs/PERFORMANCE_BASELINE.md`.
  - Configuração de matriz de compilação cruzada para módulos em Rust/Julia caso aceleradores sejam implementados.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Pipeline automatizado de empacotamento, testes de restauração a frio em runner limpo e publicação de releases versionadas do Hub.

## 6. O Que Fica Fora de Escopo
- Não configurar no CI automações de deploy em ambientes externos de produção que enviem transações reais a corretoras ou exponham chaves de terceiros.
- Não introduzir ferramentas pagas de análise estática sem discussão prévia e aprovação em ADR.

## 7. Verificação e Comandos
- **Validar sintaxe dos workflows localmente:**
  Utilizar ferramentas como `actionlint` ou validar formatação YAML:
  ```bash
  python -c "import yaml; [yaml.safe_load(open(f)) for f in ['.github/workflows/verify.yml', '.github/workflows/windows.yml']]"
  ```
