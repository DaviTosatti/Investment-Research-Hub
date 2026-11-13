# Contexto de `scripts/` — Automação, Bootstrap e Runtimes Portáteis

## 1. Missão e Objetivo (Goal)
O diretório `scripts/` reúne as ferramentas de automação operacional, scripts de configuração de ambiente de desenvolvimento, instaladores de dependências e os gerenciadores do porte nativo para Windows.
Sua missão é permitir que o repositório seja instalado, verificado e executado de ponta a ponta sem atritos tanto em ambientes Linux/CI (Bash) quanto em estações de trabalho Windows 10/11 x64 (PowerShell/CMD), garantindo a reprodutibilidade dos runtimes portáteis com checagem criptográfica de integridade.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Integridade portátil das skills:** a ordenação dos caminhos agora é explicitamente lexical POSIX, independente de Windows/Linux. Regenerados somente cinco hashes; conteúdos e espelhos preservados. `python scripts/sync_agent_skills.py --check` retorna `26 skills; ok`. O check foi incluído nos workflows Linux e Windows e em `scripts/check.sh`. As menções à falha da base abaixo são evidência histórica de E1.16, resolvida em E1.19.

- [x] **Scripts para Ambientes Linux e CI (`scripts/`):**
  - `bootstrap.sh`: Configuração inicial de ambiente, criação de venv Python com `uv`, instalação de dependências e preparação dos containers.
  - `check.sh`: Ruff, Mypy do motor `hub_finance`, Pytest, `alembic check` e testes/typecheck/lint/build web; requer ambiente e PostgreSQL preparados.
  - `sync_agent_skills.py`: Sincronização unidirecional de `.agents/skills`/`.agents/references` para `.claude/skills`/`.claude/references`. Gera/verifica `skills-lock.json`; `--check` não escreve e falha quando há divergência.
- [x] **Suporte e Porte Nativo Windows (`scripts/windows/`):**
  - `Start-Hub.ps1`: Script PowerShell mestre de inicialização dos servidores do Hub (PostgreSQL local, backend FastAPI e frontend Next.js) com detecção de runtimes e abertura automática no navegador.
  - `runtime.py`: Ponto de entrada de cinco linhas que chama `hub_api.windows_runtime.main`; download/extração estão no PowerShell, supervisão/cluster no módulo Python da API.
  - `downloads.json`: Manifesto com `schema_version`, `python_version` e `downloads` (`uv`, `node`, `postgres`, `vclibs`), URLs oficiais, SHA-256 e `archive_root`. Python é instalado pelo `uv` na versão fixada; não há Caddy nem objeto de download `python`.

Fontes: [bootstrap.sh](bootstrap.sh), [check.sh](check.sh), [sincronizador](sync_agent_skills.py), [Start-Hub.ps1](windows/Start-Hub.ps1), [entry point](windows/runtime.py), [supervisor](../apps/api/src/hub_api/windows_runtime.py) e [manifesto real](windows/downloads.json). Evidência Windows e limites de homologação constam em [WINDOWS.md](../docs/WINDOWS.md); a existência dos scripts não certifica todas as máquinas Windows 10/11.

## 3. Regras de Negócio e Invariantes dos Scripts
- **Segurança de Downloads:** Os arquivos portáteis listados em `downloads` têm SHA-256 verificado pelo PowerShell antes da extração; divergência interrompe a instalação. Python é provisionado pelo `uv` fixado, não por hash próprio de um objeto `python` no manifesto.
- **Tolerância a Caminhos Complexos:** Todos os scripts de automação Windows devem funcionar perfeitamente quando o repositório estiver clonado em diretórios com espaços em branco ou acentos (ex: `C:\Usuários\João Silva\Hub`).
- **Idempotência Operacional:** Executar `bootstrap.sh` ou `Start-Hub.ps1` repetidas vezes deve ser seguro, não deve corromper bancos existentes nem duplicar processos já ativos.
- **Nenhum Segredo em Script:** Proibido embutir senhas de banco de dados, chaves de API ou segredos nos scripts; estes devem ser gerados aleatoriamente em tempo de inicialização local ou lidos de arquivos de ambiente não versionados.

## 4. Contratos de Interface (Manifesto de Runtimes)
- Estrutura efetiva de [downloads.json](windows/downloads.json), validada por `Read-Downloads` em `Start-Hub.ps1`:

  | Campo | Contrato da base |
  | --- | --- |
  | `schema_version` | `1` |
  | `python_version` | `3.12.14`, instalado via `uv python install` |
  | `downloads` | Objetos `uv`, `node`, `postgres`, `vclibs` |
  | Cada objeto de download | `version`, `url` HTTPS oficial, `sha256`, `archive_root` |

- O PowerShell prepara runtimes e dependências com lockfiles e delega a ação a `runtime.py`; o supervisor da API gerencia perfil, banco, serviços e verificação. O sincronizador recebe `.agents` como fonte e produz espelho/lock, sem importar edições de `.claude` de volta.

## 5. Roteiro por Etapas (Ao fim das etapas)

Dependências do [plano](../docs/IMPLEMENTATION_PLAN.md) e da [matriz R31/R32/R41/R44/R47](../docs/REQUIREMENTS_MATRIX.md); os scripts futuros não estão presentes na base.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Script autônomo de backup consistente do PostgreSQL e do armazenamento entregue (originais, snapshots, artefatos e configuração), com hashes/schema e credenciais separadas; restaurar em destino vazio e verificar relações já na Etapa 1.
  - Script para exportação e importação de pacotes de dados de demonstração (seed de dados canônicos com 2 usuários e ativos da B3).
  - Validação contínua do script de sincronização de skills com parâmetro `--check` adicionado ao CI.
  - Manter a integridade portátil e o check incluídos em E1.19 ao evoluir skills e referências.
  - Comandos de operação/verificação do mecanismo durável de jobs conforme sua implementação, demonstrando reinício/retomada sem efeitos parciais antes de aceitar imports em segundo plano.
  - Scripts e execução da primeira linha de base de cargas representativas da etapa; registrar ambiente, volume, componentes, memória, variação e limites em `docs/PERFORMANCE_BASELINE.md`.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Ampliar os scripts e comparar benchmarks dos novos motores com a linha de base medida na Etapa 1 em `docs/PERFORMANCE_BASELINE.md`.
  - Scripts de compilação ou instalação das bibliotecas de cálculo aceleradas (caso Rust/Julia sejam aprovados por benefício real).
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Scripts de recuperação de desastres a frio a partir de ambientes sem nenhuma dependência pré-instalada.
  - Rotinas para atualização automática do Hub sem perda de configurações locais e transações anteriores.

## 6. O Que Fica Fora de Escopo
- Não usar os scripts para baixar pacotes de dependências ou dados de mercado sem rastreabilidade de fonte.
- Não manter scripts que executem comandos destrutivos sem confirmação explícita do usuário (`rm -rf` indiscriminado ou drop de banco).

## 7. Verificação e Comandos
- **Verificar integridade e sincronismo das skills:**
  ```bash
  python scripts/sync_agent_skills.py --check
  ```
  Após E1.19, retorna `26 skills; ok`, exit 0; a [auditoria F09](../docs/CONTEXT_PLAN_COMPARISON.md) preserva o diagnóstico histórico dos cinco hashes.
- **Executar suíte de validação Linux:**
  ```bash
  bash scripts/check.sh
  ```
- **Verificar ambiente nativo Windows:**
  Executar o atalho `Verificar Hub.cmd` na raiz do projeto.
