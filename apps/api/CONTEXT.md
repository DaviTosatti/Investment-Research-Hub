# Contexto de `apps/api` — Servidor HTTP REST e Persistência

## 1. Missão e Objetivo (Goal)
O `apps/api` provê a API REST institucional (`/api/v1`) do Hub construída sobre FastAPI, SQLAlchemy 2.0 e PostgreSQL. Ele é responsável por:
1. Gerenciar autenticação com sessões seguras e controle de acesso baseado em papéis (`admin`, `member`, `viewer`).
2. Preservar a titularidade econômica e a autoria dos registros, com consulta compartilhada no grupo e escrita controlada por papel.
3. Orquestrar a persistência append-only de eventos, lançamentos e avaliações manuais; o `snapshot_id` do dashboard é checksum da consulta, sem snapshot completo persistido/recuperável por versão na base.
4. Invocar `hub_finance` para posições e caixa; calcular avaliações e agregações no serviço de portfólio existente.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Núcleo da Aplicação (`src/hub_api/`):**
  - `main.py`: Inicialização do FastAPI, middlewares de segurança (`X-Hub-Request`, headers HTTP), montagem das rotas.
  - `models.py`: Tabelas relacionais declaradas no SQLAlchemy (`User`, `AuthSession`, `LoginAttempt`, `Owner`, `Account`, `Portfolio`, `Issuer`, `Instrument`, `Listing`, `Price`, `Transaction`, `JournalEntry`, `AuditEvent`). A base de identidade não resolve identificadores oficiais, vigências ou histórico de símbolos.
  - `schemas.py`: Modelos Pydantic v2 de entrada, com validação de payloads e rejeição de números JSON para campos Decimal.
  - `portfolio_service.py`: Replay via `hub_finance.ledger`, seleção de avaliações, custo médio, valor de mercado, resultado não realizado, histórico a custo e agregações Decimal.
  - `security.py`: Hashing com `argon2-cffi`, sessões, papéis, limite de tentativas e verificação com hash fictício quando o usuário não existe.
  - `config.py`: Gestão de configurações e variáveis de ambiente tipadas.
  - `errors.py`: Define `AppError` e mensagens de validação de contas; handlers em `main.py` convertem exceções para `{error: {code, message}}`.
  - `responses.py`: Schemas de resposta tipados com Decimal serializado como string e paginação (`{items, total, limit, offset}`); a montagem da página ocorre em `main.py`.
  - `cli.py`: Comandos administrativos `create-admin` e `setup-admin`, com entrada privada/interativa de senha.
  - `windows_runtime.py`: Utilitários para inicialização limpa e supervisão no Windows.
- [x] **Rotas HTTP da base (14 caminhos, 19 operações em `main.py`):**
  - Sistema: `GET /api/v1/health`, `GET /api/v1/openapi.json`
  - Autenticação: `POST /api/v1/auth/login`, `GET /api/v1/auth/session`, `POST /api/v1/auth/logout`
  - Membros e Titulares: `GET/POST /api/v1/members`, `GET/POST /api/v1/owners`
  - Carteiras e Ativos: `GET/POST /api/v1/portfolios`, `GET/POST /api/v1/instruments`
  - Cotações e Operações: `POST /api/v1/prices`, `GET/POST /api/v1/transactions`
  - Painel e Auditoria: `GET /api/v1/dashboard`, `GET /api/v1/reports/positions.csv`, `GET /api/v1/audit`
- [x] **Ingestão guiada de operações (`import_*.py`):**
  - Upload CSV/XLSX limitado, original privado com SHA-256, fontes de arquivos, prévias imutáveis, correções antes da confirmação, quarentena e decisões de duplicatas.
  - Rotas adicionais: `GET/POST /sources`, `GET/POST /imports`, `GET /imports/{id}`, `GET /imports/{id}/original`, `POST /imports/{id}/preview`, `POST /imports/{id}/confirm`, `GET /snapshots`, `GET /snapshots/{id}`, `GET /quality`, `GET /lineage`. Total com a base: 24 caminhos/31 operações.
  - `transaction_service.py` é o caminho compartilhado com operações manuais; confirmação atômica, lock por carteira e recusa de prévia desatualizada. [Contrato e limites](../../docs/IMPORTS.md).
  - Novas tabelas: `DataSource`, `OriginalFile`, `ImportBatch`, `ImportPreview`, `ImportReceipt`. Não implementam provedores externos, jobs ou retificação de operações já lançadas.
- [x] **Migrações de Banco de Dados (`migrations/`):**
  - `fde27e01f059_create_foundation_tables.py`: Criação das tabelas base.
  - `0002_ledger_integrity.py`: Triggers que impedem alteração/exclusão do histórico e exigem lançamentos balanceados no commit; unicidade de idempotência/identificador externo vem da migração inicial.

Fontes: [main.py](src/hub_api/main.py), [modelos](src/hub_api/models.py), [security.py](src/hub_api/security.py), [serviço de portfólio](src/hub_api/portfolio_service.py), [CLI](src/hub_api/cli.py) e [migração de integridade](migrations/versions/0002_ledger_integrity.py). Este inventário conserva a base anterior à integração de ingestão; ver [auditoria F01/F04/F05/F13](../../docs/CONTEXT_PLAN_COMPARISON.md).

## 3. Contrato Local: Inputs, Process e Outputs

### Inputs (Entradas e o que ler)
- **Leitura obrigatória antes de editar:** [docs/API_CONTRACT.md](../../docs/API_CONTRACT.md) e o esquema de banco em `src/hub_api/models.py`.
- **Payloads recebidos:** JSON validado via [schemas.py](src/hub_api/schemas.py), com decimais em strings (até 8 casas para quantidades/preços; caixa, taxas e tributos em BRL exigem centavos no ledger) e datas ISO 8601 (`YYYY-MM-DD`).
- **Autenticação e Cabeçalhos:** Cookie de sessão `hub_session` obrigatório (exceto login/health) e header `X-Hub-Request: 1` em todas as requisições de escrita (`POST`, `PUT`, `DELETE`).

### Process (Fluxo e como trabalhar)
1. Para novas entidades ou alterações de esquema:
   - Declarar modelos em `models.py` com tipagem SQLAlchemy 2.0 (`Mapped[...]`).
   - Gerar e revisar migração com `alembic revision --autogenerate -m "..."`.
   - Adicionar ou atualizar schemas Pydantic em `schemas.py`.
2. Para cálculos contábeis ou de custódia:
   - Delegar eventos, caixa e custo ao `hub_finance.ledger`. Reutilizar avaliações/agregações existentes em `portfolio_service.py`, sem criar fórmulas concorrentes em rotas, frontend ou exportadores.
3. Para persistência de transações:
   - Bloquear a carteira antes de ler saldo/idempotência. A mesma chave por carteira (ou `source`/`external_id`) com payload canônico equivalente retorna o evento existente (200); divergência retorna 409. A base exige ordem cronológica e ainda não oferece retificação histórica.
   - Usar `AppError` para erros de serviço e `LedgerError` para o ledger; os handlers em `main.py` os convertem em `{error: {code, message}}`.

### Outputs (Entregas e saídas esperadas)
- Respostas padronizadas via `responses.py`:
  - Entidades de usuário/titular/carteira/ativo/preço/transação com IDs UUID e datas ISO 8601; auditoria usa ID sequencial convertido para string na resposta.
  - Listas paginadas no formato institucional: `{items: [...], total: int, limit: int, offset: int}`.
- Status da base incluem `200`, `201`, `204`, `401`, `403`, `404`, `409`, `422`, `429` (limite de login) e `503` (banco indisponível).
- Auditoria: cadastros/eventos e login/logout bem-sucedidos registram `AuditEvent` append-only com `actor_id`; isso não significa que toda entidade tenha `created_by` ou que toda tentativa rejeitada gere evento de auditoria.
- Dashboard/CSV compartilham leitura `REPEATABLE READ`, método e filtros. Limites da base: BRL, caixa por negociação, até 20 mil eventos por consulta, histórico a custo com revisões hoje conhecidas e `performance: null`; não é backtest com disponibilidade histórica.

## 4. Regras de Negócio e Invariantes Locais (Layer 5)
- **Contabilidade Imutável:** Transações, lançamentos, preços e auditoria são append-only por migração. Correções deverão usar eventos estornadores/retificadores versionados; esse fluxo ainda é pendência da Etapa 1, não endpoint implementado.
- **Idempotência Obrigatória:** Escritas em `/api/v1/transactions` requerem `idempotency_key`.
- **Decimal como String:** Valores monetários trafegam como strings. Quantidades/preços admitem até 8 casas; taxas/tributos e fluxos de caixa BRL são validados em centavos pelo ledger. O banco usa `NUMERIC(38,16)` para valores contábeis.
- **Titularidade e Permissões:** `admin` e `member` podem registrar dados do grupo; somente `admin` cria membros. `viewer` consulta sem escrita financeira. `require_writer` verifica papel, sem tabela/ACL usuário–titular. Os vínculos conta/carteira/operação preservam titularidade econômica, não isolamento de leitura entre amigos autorizados (Promptx §0; matriz T29/T30).
- **Transações Sem Ordem:** Operações são fatos econômicos consumados. Não existe endpoint para cancelamento direto de ordem ou envio a corretoras.

## 5. Roteiro por Etapas (Ao fim das etapas)

Rotas abaixo são propostas sob `/api/v1`, sujeitas ao [plano](../../docs/IMPLEMENTATION_PLAN.md) e à [matriz](../../docs/REQUIREMENTS_MATRIX.md); não compõem o inventário implementado acima.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Ampliar as rotas `/sources`, `/imports`, `/snapshots`, `/quality`, `/lineage`, já existentes para extratos: identidade oficial/vigências, fontes externas reais verificadas, normalização de unidades/períodos e revisões com cutoff de disponibilidade para dados de mercado/fundamentos.
  - Completar a cobertura integral do importador CSV/XLSX além do fluxo limitado entregue: retificação/estorno de eventos já confirmados com origem, decisões e impacto rastreáveis; trabalhos extensos dependem de jobs duráveis.
  - S01: saldos iniciais identificados, transferências, câmbio, proventos, metas e performance canônica (TWR/MWR ou aproximação explicitamente nomeada), conciliada com dashboard e relatórios.
  - S02/S03/S07: mercado/watchlists (`/market`, `/watchlists`), fundamentos/TTM/setores (`/issuers`, `/analyses/fundamentals`) e macro (`/macro`), com fonte, períodos, qualidade S12 e disponibilidade histórica.
  - S23: aprendizado/glossário/exemplos executados (`/learning`) com os motores canônicos; diário/teses/comentários básicos com autoria, original e versões preservados.
  - Servidor de relatórios completos (PDF/XLSX além do CSV existente) via S21.
  - Interface do protocolo MCP (Model Context Protocol) para consumo do Hub por LLMs.
  - Persistência e execução durável de jobs (`/jobs`) antes de aceitar trabalho em segundo plano: lease/heartbeat, retentativas limitadas, retomada, estados e cancelamento explícito, com efeitos financeiros atômicos (matriz R31/R32).
  - Backup/restauração inicial em destino vazio, manifesto dos motores e primeira linha de base medida; procedimentos, wrappers, avaliações das sete skills e jornadas A/recortes B/F integrados às 12 páginas-base.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Rotas que atendem às 12 skills avançadas, reutilizando motores comuns: `/analyses/valuation`, `/analyses/fixed-income`, `/analyses/etfs`, `/analyses/risk`, `/analyses/simulations`, `/analyses/optimization`, `/analyses/backtests`, `/screeners`, `/tax`.
  - Versionamento de premissas e notas de valuation.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Endpoints do Comitê de IA (`/committee`), auditoria de divergências e sínteses salvas.
  - Endpoints de alertas (`/alerts`), agendamentos (`/schedules`) e reconciliação de eventos oficiais de bolsa (`/events`).

## 6. O Que Fica Fora de Escopo
- Não duplicar cálculos financeiros em novas rotas; reutilizar `hub_finance` e `portfolio_service.py` conforme a fronteira atual.
- Swagger/ReDoc estão desativados; consultar `/api/v1/openapi.json` autenticado, não `/openapi.json`.
- Nenhum envio de ordens de compra/venda para corretoras ou exchanges.

## 7. Verificação e Comandos
- **Testes de Integração PostgreSQL:**
  ```bash
  pytest tests/integration -v
  ```
- **Linters e Checagem Estática (ambiente instalado a partir da raiz):**
  ```bash
  ruff check apps/api
  mypy
  ```
  O Mypy sem caminhos verifica apenas `hub_finance`, conforme [pyproject.toml](../../pyproject.toml) e [CI](../../.github/workflows/verify.yml). A ampliação à API é pendente: a auditoria F11 registrou 136 erros em 7 arquivos para `mypy apps/api/src`; não são falhas de execução da API nem um gate aprovado.
- **Verificação de Migrações do Banco:**
  ```bash
  alembic check
  ```
  Integração requer PostgreSQL disponível e permissão de criar/remover o banco temporário de testes; `alembic check` requer banco alvo migrado e configurado.
