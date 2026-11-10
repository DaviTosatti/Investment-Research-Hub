# Contexto de `scripts/` — Automação, Bootstrap e Runtimes Portáteis

## 1. Missão e Objetivo (Goal)
O diretório `scripts/` reúne as ferramentas de automação operacional, scripts de configuração de ambiente de desenvolvimento, instaladores de dependências e os gerenciadores do porte nativo para Windows.
Sua missão é permitir que o repositório seja instalado, verificado e executado de ponta a ponta sem atritos tanto em ambientes Linux/CI (Bash) quanto em estações de trabalho Windows 10/11 x64 (PowerShell/CMD), garantindo a reprodutibilidade dos runtimes portáteis com checagem criptográfica de integridade.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Scripts para Ambientes Linux e CI (`scripts/`):**
  - `bootstrap.sh`: Configuração inicial de ambiente, criação de venv Python com `uv`, instalação de dependências e preparação dos containers.
  - `check.sh`: Esteira de validação completa para Linux: linters (Ruff), checagem de tipos (Mypy), testes de unidade e integração.
  - `sync_agent_skills.py`: Sincronizador bidirecional entre as skills canônicas em `.agents/skills` e o espelho do Claude Code em `.claude/skills`. Gera e verifica o lockfile criptográfico `skills-lock.json`.
- [x] **Suporte e Porte Nativo Windows (`scripts/windows/`):**
  - `Start-Hub.ps1`: Script PowerShell mestre de inicialização dos servidores do Hub (PostgreSQL local, backend FastAPI e frontend Next.js) com detecção de runtimes e abertura automática no navegador.
  - `runtime.py`: Orquestrador Python autônomo responsável pelo download, extração, configuração de caminhos e inicialização do cluster PostgreSQL nativo do Windows.
  - `downloads.json`: Manifesto de dependências portáteis para Windows (Python, PostgreSQL, Node.js, Caddy) com URLs oficiais e hashes criptográficos SHA-256 fixos.

## 3. Regras de Negócio e Invariantes dos Scripts
- **Segurança de Downloads:** Nenhum binário ou runtime é executado no Windows sem que seu hash SHA-256 seja validado contra o `downloads.json`. Se o hash diferir, o script interrompe a execução com erro fatal.
- **Tolerância a Caminhos Complexos:** Todos os scripts de automação Windows devem funcionar perfeitamente quando o repositório estiver clonado em diretórios com espaços em branco ou acentos (ex: `C:\Usuários\João Silva\Hub`).
- **Idempotência Operacional:** Executar `bootstrap.sh` ou `Start-Hub.ps1` repetidas vezes deve ser seguro, não deve corromper bancos existentes nem duplicar processos já ativos.
- **Nenhum Segredo em Script:** Proibido embutir senhas de banco de dados, chaves de API ou segredos nos scripts; estes devem ser gerados aleatoriamente em tempo de inicialização local ou lidos de arquivos de ambiente não versionados.

## 4. Contratos de Interface (Manifesto de Runtimes)
- O arquivo `downloads.json` define a lista de runtimes portáteis requeridos no Windows:
  ```json
  {
    "python": {
      "version": "3.12.x",
      "url": "https://...",
      "sha256": "..."
    },
    "postgresql": {
      "version": "17.x",
      "url": "https://...",
      "sha256": "..."
    }
  }
  ```

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Script autônomo para realização de backup e restauração consistente do banco PostgreSQL local.
  - Script para exportação e importação de pacotes de dados de demonstração (seed de dados canônicos com 2 usuários e ativos da B3).
  - Validação contínua do script de sincronização de skills com parâmetro `--check` adicionado ao CI.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Scripts de benchmarking de desempenho para medir tempos de cálculo dos motores financeiros e registrar a linha de base em `docs/PERFORMANCE_BASELINE.md`.
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
- **Executar suíte de validação Linux:**
  ```bash
  bash scripts/check.sh
  ```
- **Verificar ambiente nativo Windows:**
  Executar o atalho `Verificar Hub.cmd` na raiz do projeto.
