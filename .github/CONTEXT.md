# Contexto de `.github/` — Integração Contínua (CI), Automações e Pull Requests

## 1. Missão e Objetivo (Goal)
O diretório `.github/` abriga os fluxos de trabalho de Integração Contínua (CI), automações de checagem de qualidade e templates de Pull Request do repositório no GitHub.
Sua missão é executar os checks de qualidade e apoiar a política de integrar incrementos verificados: lint, tipos no escopo configurado, testes Python com PostgreSQL real, build web e verificação Windows. Workflows existentes não comprovam proteção obrigatória de branch, implantação em produção ou cobertura integral de tipos/testes.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Integridade portátil das skills:** a ordenação dos caminhos agora é explicitamente lexical POSIX, independente de Windows/Linux. Regenerados somente cinco hashes; conteúdos e espelhos preservados. `python scripts/sync_agent_skills.py --check` retorna `26 skills; ok`. O check foi incluído nos workflows Linux e Windows e em `scripts/check.sh`. As menções à falha da base abaixo são evidência histórica de E1.16, resolvida em E1.19.

- [x] **Workflows do GitHub Actions (`workflows/`):**
  - `verify.yml`: Workflow principal em Linux contendo dois jobs paralelos:
    - `api`: Em Ubuntu, provisiona PostgreSQL 17.6, prepara Python 3.12 e dependências com `uv`, aplica/confere migrações Alembic, executa Ruff, `uv run mypy` (somente `hub_finance`) e Pytest (`tests/unit` e `tests/integration`).
    - `web`: Instala dependências com `npm ci`, roda checagem de tipos TypeScript (`npm run typecheck`), linter (`npm run lint`), testes unitários (`npm run test`) e build de produção (`npm run build`).
  - `windows.yml`: Job `native` em Windows Server 2022 x64 que executa bootstrap, verificação nativa e testes em caminho com acentos/espaços; publica artefato de fontes/atalhos versionados com retenção de 30 dias, não release automática. Hashes dos downloads são verificados no bootstrap PowerShell.
- [x] **Templates de Governança (`pull_request_template.md`):**
  - Solicita problema/comportamento, etapa/requisitos cobertos, verificações/resultados e limites/pendências/efeito em dados/migrações; orienta atualizar STATUS e lembra que incremento não conclui skill/etapa.

Fontes: [verify.yml](workflows/verify.yml), [windows.yml](workflows/windows.yml), [template de PR](pull_request_template.md), [escopo Mypy](../pyproject.toml) e [auditoria F09/F11/F14](../docs/CONTEXT_PLAN_COMPARISON.md). Proteções remotas de branch não foram auditadas.

## 3. Regras de Negócio e Invariantes do CI
- **Proibição Estrita de Force Push:** É expressamente vedado o uso de `git push --force` ou reescrita de histórico já publicado no repositório remoto.
- **Padrão Conventional Commits:** Todas as mensagens de commit e títulos de PRs devem seguir a convenção formal:
  - `feat(<escopo>): ...` — Novas funcionalidades.
  - `fix(<escopo>): ...` — Correções de bugs.
  - `docs(<escopo>): ...` — Documentação e contextos ICM.
  - `test(<escopo>): ...` — Adição ou ajuste de testes.
  - `chore(<escopo>): ...` — Ajustes de dependências e tooling.
  - `ci(<escopo>): ...` — Alterações em pipelines do GitHub Actions.
- **Proibição de Bypass de Quality Gates:** Como política do projeto, PRs com falha em `api`, `web` ou `native` não devem ser mesclados; exigibilidade automática depende das regras remotas de branch.
- **Proteção de Segredos:** O CI não deve expor credenciais reais em logs. A base usa também valores sintéticos fixos para PostgreSQL/fixtures de teste, além de valores gerados pelo runtime; não afirmar que todos são gerados em memória nem reproduzir credenciais pessoais.

## 4. Contratos de Execução dos Workflows
- **Trigger:** Ambos disparam em `push` e `pull_request`, sem filtros de branches; `windows.yml` também oferece `workflow_dispatch`.
- **PostgreSQL em CI:** O job `api` obrigatoriamente provisiona um container oficial de PostgreSQL com as credenciais padrão de teste, garantindo paridade com os testes locais.

## 5. Roteiro por Etapas (Ao fim das etapas)

Pendências do [plano](../docs/IMPLEMENTATION_PLAN.md) e da [matriz](../docs/REQUIREMENTS_MATRIX.md); existência de um pipeline não equivale a aprovação dos portões.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Adição de step no workflow `verify.yml` para rodar `python scripts/sync_agent_skills.py --check`, garantindo que o lockfile e o espelho das skills de IA nunca cheguem desatualizados ao repositório.
  - Adição de checagem automática de links quebrados nos arquivos de documentação (`docs/`).
  - Preservar a correção portátil e os checks de skills integrados aos workflows em E1.19.
  - Evidência de execução durável/retomada de jobs, reimportação/reconciliação, qualidade e recuperação inicial: backup/restauração de banco e artefatos entregues em destino vazio já na Etapa 1, sem depender do pipeline ampliado da Etapa 3.
  - Registrar a primeira linha de base medida e os checks pertinentes às sete skills/12 páginas/jornadas da etapa; ampliar tipagem da API como pendência distinta do Mypy do motor. Verificar/configurar gates obrigatórios conforme a política do projeto, sem presumir proteção remota existente.
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
  Se `actionlint` estiver instalado, validar os workflows:
  ```bash
  actionlint .github/workflows/verify.yml .github/workflows/windows.yml
  ```
  `actionlint` não é dependência do manifesto Python. Parsing YAML isolado não valida semântica do GitHub Actions nem comprova execução remota; os comandos efetivos estão nos workflows citados.
