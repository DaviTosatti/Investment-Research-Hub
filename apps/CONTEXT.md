# Contexto de `apps/` — Aplicações e Processos Executáveis

## 1. Missão e Objetivo (Goal)
O diretório `apps/` abriga os processos de execução do Investment Research Hub que rodam servidores ou clientes independentes. Ele isola as responsabilidades de protocolo (HTTP REST, Web SPA/SSR) e mantém os limites de arquitetura limpos: **nenhuma regra contábil ou financeira é calculada diretamente dentro de `apps/`** — todas as regras e lógicas de cálculo residem em `packages/engines/`.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] [`api/`](api/CONTEXT.md) — Backend em Python (FastAPI, SQLAlchemy, Alembic, PostgreSQL). Provê a API REST institucional sob `/api/v1`.
- [x] [`web/`](web/CONTEXT.md) — Frontend em TypeScript e Next.js (App Router, Tailwind CSS). Interface fintech escura aprovada pelo usuário.

## 3. Regras de Negócio e Invariantes Locais
- **Compartilhamento Obrigatório do Motor:** Tanto a `api` quanto futuros exportadores, servidores MCP e workers em `apps/` devem obrigatoriamente importar e reutilizar as funções determinísticas de `hub_finance` (`packages/engines/`). Proibida a reimplementação de fórmulas em TypeScript ou endpoints ad-hoc.
- **Protocolo de Comunicação Padronizado:** O canal oficial de comunicação entre `web` e `api` é exclusivamente a rota `/api/v1` conforme documentado em [docs/API_CONTRACT.md](../docs/API_CONTRACT.md).
- **Sem CORS Agressivo e Sem Mocks na API:** A comunicação web/api roda orientada a cookies de sessão `HttpOnly` com validação de cabeçalho `X-Hub-Request: 1`. Endpoints não devem mockar dados para "parecer pronto" se a regra de persistência e auditoria não existir.

## 4. Contratos de Interface entre as Apps
- **Autenticação:** Cookie HttpOnly gerado em `/api/v1/auth/login` consumido pelo Next.js (SSR ou client-side fetch).
- **Contrato de Números:** A `api` serializa números decimais em strings nos payloads JSON (`"1500.50"`). O `web` exibe essas strings formatadas com funções em `apps/web/src/lib/format.ts`, sem converter para `float`/`number` do JavaScript para cálculos.
- **Identidade vs Listagem:** O frontend referencia ativos financeiros por seus `id` imutáveis (UUID), e nunca puramente por `ticker`, pois tickers podem mudar de bolsa, sofrer renomeação ou reuso.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - `apps/api` e `apps/web` cobrindo com dados reais persistidos as 12 páginas-base (P01 Início, P02 Aprender, P03 Mercado, P04 Ações, P08 Macro, P10 Carteiras, P11 Operações, P12 Proventos, P19 Diário, P21 Relatórios, P22 Dados, P23 Administração).
  - Implementação do servidor de relatórios (CSV, PDF) e servidor MCP inicial.
  - Mecanismo de persistência de jobs assíncronos básicos.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - `apps/web` e `apps/api` ampliadas para suportar as telas analíticas avançadas: P05 FIIs, P06 Renda Fixa, P07 ETFs/Globais, P09 Valuation, P13 Tributação, P14 Riscos, P15 Otimização, P16 Backtesting, P17 Radar.
  - Endpoints analíticos com histórico de premissas e versões editáveis.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Criação de novo processo independente `apps/worker/` caso a carga de jobs em background, ingestão contínua e inferência de IA justifique a separação física do processo da API.
  - `apps/web` com suporte a colaboração multiusuário em tempo real, tela P18 Comitê IA e P20 Alertas/Monitoramento.
  - Conexão e sincronização perfeita entre as 23 páginas e 23 skills.

## 6. O Que Fica Fora de Escopo
- Não criar pastas `apps/worker` ou `apps/mcp` enquanto não houver código real e testes correspondentes.
- Não colocar scripts utilitários ou de setup dentro de `apps/` (esses pertencem a `scripts/`).

## 7. Verificação
- **API:** Consulte [apps/api/CONTEXT.md](api/CONTEXT.md) para os comandos de Pytest e migrações.
- **Web:** Consulte [apps/web/CONTEXT.md](web/CONTEXT.md) para typecheck, lint, testes Vitest e build Next.js.
