# Contexto de `apps/api` — Servidor HTTP REST e Persistência

## 1. Missão e Objetivo (Goal)
O `apps/api` provê a API REST institucional (`/api/v1`) do Hub construída sobre FastAPI, SQLAlchemy 2.0 e PostgreSQL. Ele é responsável por:
1. Gerenciar autenticação com sessões seguras e controle de acesso baseado em papéis (`admin`, `member`, `viewer`).
2. Garantir o isolamento de dados por titular econômico (`owner_id`) e a trilha de auditoria (`created_by`).
3. Orquestrar a persistência imutável dos eventos do ledger financeiro e o snapshot de cotações manuais.
4. Invocar o motor `hub_finance` para gerar posições derivadas e saldo em caixa sob demanda.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Núcleo da Aplicação (`src/hub_api/`):**
  - `main.py`: Inicialização do FastAPI, middlewares de segurança (`X-Hub-Request`, headers HTTP), montagem das rotas.
  - `models.py`: Tabelas relacionais declaradas no SQLAlchemy (`User`, `Owner`, `Portfolio`, `Instrument`, `Price`, `Transaction`, `AuditLog`).
  - `schemas.py`: Modelos Pydantic v2 com serialização Decimal estrita e validação de payloads.
  - `portfolio_service.py`: Camada de serviço que faz a ponte entre o banco relacional e o motor `hub_finance.ledger`.
  - `security.py`: Hashing seguro de senhas com `argon2-cffi`, controle de cookies de sessão e proteção contra timing attacks.
  - `config.py`: Gestão de configurações e variáveis de ambiente tipadas.
  - `errors.py`: Mapeamento de exceções de domínio para erros HTTP padronizados (`{error: {code, message}}`).
  - `responses.py`: Padrão de paginação institucional (`{items, total, limit, offset}`).
  - `cli.py`: Comandos de linha de comando para tarefas administrativas (ex: `bootstrap-admin`).
  - `windows_runtime.py`: Utilitários para inicialização limpa e supervisão no Windows.
- [x] **Rotas HTTP Implementadas (14 caminhos, 19 operações):**
  - Sistema: `GET /api/v1/health`, `GET /api/v1/openapi.json`
  - Autenticação: `POST /api/v1/auth/login`, `GET /api/v1/auth/session`, `POST /api/v1/auth/logout`
  - Membros e Titulares: `GET/POST /api/v1/members`, `GET/POST /api/v1/owners`
  - Carteiras e Ativos: `GET/POST /api/v1/portfolios`, `GET/POST /api/v1/instruments`
  - Cotações e Operações: `POST /api/v1/prices`, `GET/POST /api/v1/transactions`
  - Painel e Auditoria: `GET /api/v1/dashboard`, `GET /api/v1/reports/positions.csv`, `GET /api/v1/audit`
- [x] **Migrações de Banco de Dados (`migrations/`):**
  - `fde27e01f059_create_foundation_tables.py`: Criação das tabelas base.
  - `0002_ledger_integrity.py`: Constraints de unicidade e integridade contábil.

## 3. Contrato Local: Inputs, Process e Outputs

### Inputs (Entradas e o que ler)
- **Leitura obrigatória antes de editar:** [docs/API_CONTRACT.md](../../docs/API_CONTRACT.md) e o esquema de banco em `src/hub_api/models.py`.
- **Payloads recebidos:** JSON estritamente tipado via Pydantic (`schemas.py`), com números decimais em strings (até 8 casas) e datas em ISO 8601 (`YYYY-MM-DD`).
- **Autenticação e Cabeçalhos:** Cookie de sessão `hub_session` obrigatório (exceto login/health) e header `X-Hub-Request: 1` em todas as requisições de escrita (`POST`, `PUT`, `DELETE`).

### Process (Fluxo e como trabalhar)
1. Para novas entidades ou alterações de esquema:
   - Declarar modelos em `models.py` com tipagem SQLAlchemy 2.0 (`Mapped[...]`).
   - Gerar e revisar migração com `alembic revision --autogenerate -m "..."`.
   - Adicionar ou atualizar schemas Pydantic em `schemas.py`.
2. Para cálculos contábeis ou de custódia:
   - Nunca calcular em rotas ou serviços da API; delegar a `hub_finance.ledger` (`packages/engines`).
3. Para persistência de transações:
   - Validar `idempotency_key`. Garantir que se a mesma chave for enviada com payload idêntico, retorne o evento existente; com payload divergente, retorne HTTP 409 Conflict.
   - Tratar erros de domínio com exceções de `errors.py`, convertendo-as em respostas `{error: {code, message}}`.

### Outputs (Entregas e saídas esperadas)
- Respostas padronizadas via `responses.py`:
  - Recursos unitários com IDs UUID e datas ISO 8601.
  - Listas paginadas no formato institucional: `{items: [...], total: int, limit: int, offset: int}`.
- Códigos de status HTTP canônicos: `200 OK`, `201 Created`, `204 No Content`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`.
- Auditoria: toda operação de mutação gera registro append-only em `AuditLog`.

## 4. Regras de Negócio e Invariantes Locais (Layer 5)
- **Contabilidade Imutável:** Transações registradas são append-only. Correções financeiras nunca fazem `UPDATE` ou `DELETE` no valor ou evento; exigem um novo evento estornador ou retificador.
- **Idempotência Obrigatória:** Escritas em `/api/v1/transactions` requerem `idempotency_key`.
- **Decimal como String:** Nenhum valor monetário trafega como float. Entradas aceitam até 8 casas decimais (`quantity`, `unit_price`, `fees`, `taxes`); saídas sempre formatadas com ponto decimal.
- **Isolamento de Titularidade Econômica:** Usuários da role `member` só inserem operações para carteiras associadas aos seus titulares autorizados. Usuários `viewer` têm acesso estritamente somente-leitura.
- **Transações Sem Ordem:** Operações são fatos econômicos consumados. Não existe endpoint para cancelamento direto de ordem ou envio a corretoras.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Implementação das rotas de ingestão de dados e quarentena: `/sources`, `/imports`, `/snapshots`, `/quality`, `/lineage`.
  - Importador de extratos CSV/XLSX com reconciliação e detecção de duplicatas.
  - Servidor de relatórios completos (PDF/XLSX além do CSV existente) via S21.
  - Interface do protocolo MCP (Model Context Protocol) para consumo do Hub por LLMs.
  - Persistência e acompanhamento de jobs assíncronos (`/jobs`).
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Rotas dos 12 motores avançados: `/analyses/valuation`, `/analyses/fixed-income`, `/analyses/etfs`, `/analyses/risk`, `/analyses/simulations`, `/analyses/optimization`, `/analyses/backtests`, `/screeners`, `/tax`.
  - Versionamento de premissas e notas de valuation.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Endpoints do Comitê de IA (`/committee`), auditoria de divergências e sínteses salvas.
  - Endpoints de alertas (`/alerts`), agendamentos (`/schedules`) e reconciliação de eventos oficiais de bolsa (`/events`).

## 6. O Que Fica Fora de Escopo
- Não implementar lógicas de cálculo financeiro direto em rotas ou serviços; invocar `hub_finance`.
- Swagger interativo (`/docs`) deve permanecer desativado por política de segurança; use `/openapi.json`.
- Nenhum envio de ordens de compra/venda para corretoras ou exchanges.

## 7. Verificação e Comandos
- **Testes de Integração PostgreSQL:**
  ```bash
  pytest tests/integration -v
  ```
- **Linters e Checagem Estática:**
  ```bash
  ruff check apps/api
  mypy apps/api/src
  ```
- **Verificação de Migrações do Banco:**
  ```bash
  alembic check
  ```
