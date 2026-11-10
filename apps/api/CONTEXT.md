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

## 3. Regras de Negócio e Invariantes Locais
- **Contabilidade Imutável:** Transações registradas são append-only. Correções financeiras nunca fazem `UPDATE` ou `DELETE` no valor ou evento; exigem um novo evento estornador ou retificador.
- **Idempotência Obrigatória:** Escritas em `/api/v1/transactions` requerem `idempotency_key`. O reenvio do mesmo payload com a mesma chave retorna o recurso original; reenvio com payload diferente resulta em `409 Conflict`.
- **Decimal como String:** Nenhum valor monetário trafega como float. Entradas aceitam até 8 casas decimais (`quantity`, `unit_price`, `fees`, `taxes`); saídas sempre formatadas com ponto decimal.
- **Isolamento de Titularidade Econômica:** Usuários da role `member` só inserem operações para carteiras associadas aos seus titulares autorizados. Usuários `viewer` têm acesso estritamente somente-leitura.
- **Transações Sem Ordem:** Operações são fatos econômicos consumados. Não existe endpoint para cancelamento direto de ordem ou envio a corretoras.

## 4. Contratos de Interface (Inputs, Process, Outputs)
- **Headers:** Todas as requisições de escrita (`POST`, `PUT`, `DELETE`) devem enviar o header `X-Hub-Request: 1`.
- **Contrato de Erro:**
  ```json
  {
    "error": {
      "code": "INSUFFICIENT_CASH",
      "message": "Saldo em caixa insuficiente para liquidar a operação."
    }
  }
  ```
- **Paginação:**
  ```json
  {
    "items": [...],
    "total": 120,
    "limit": 50,
    "offset": 0
  }
  ```
- **Contrato Completo:** Detalhes formais em [docs/API_CONTRACT.md](../../docs/API_CONTRACT.md) e esquema interativo em `/api/v1/openapi.json`.

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
