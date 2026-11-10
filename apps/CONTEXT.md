# Contexto de `apps/` — Aplicações e Processos Executáveis

## 1. Missão e Objetivo (Goal)
O diretório `apps/` abriga os processos de execução do Investment Research Hub que rodam servidores ou clientes independentes e suas responsabilidades de protocolo (HTTP REST, Web SPA/SSR). O ledger reside em `packages/engines/`; a API também calcula avaliações, custo médio, resultado não realizado e agregações em [portfolio_service.py](api/src/hub_api/portfolio_service.py). Essa é a fronteira implementada a reutilizar pelos demais canais.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] Fluxo integrado CSV/XLSX em `/dados#importacoes`: frontend e API compartilham o motor de operações, com originais privados e confirmação auditável. Consulte [IMPORTS](../docs/IMPORTS.md); fontes externas, jobs e retificação de eventos já lançados continuam no roteiro.
- [x] [`api/`](api/CONTEXT.md) — Backend em Python (FastAPI, SQLAlchemy, Alembic, PostgreSQL). Provê a API REST institucional sob `/api/v1`.
- [x] [`web/`](web/CONTEXT.md) — Frontend em TypeScript, Next.js 16.4.5/React 19.3.1 (App Router) e CSS próprio, conforme [package.json](web/package.json) e [globals.css](web/src/app/globals.css). As referências fintech escuras foram aprovadas; a homologação visual das telas permanece pendente.

## 3. Regras de Negócio e Invariantes Locais
- **Compartilhamento Obrigatório do Motor:** API, exportadores, MCP e workers devem reutilizar `hub_finance` e os serviços canônicos existentes. MCP e workers ainda não estão implementados na base. Proibida a reimplementação de fórmulas em TypeScript ou endpoints ad-hoc.
- **Protocolo de Comunicação Padronizado:** O canal oficial de comunicação entre `web` e `api` é exclusivamente a rota `/api/v1` conforme documentado em [docs/API_CONTRACT.md](../docs/API_CONTRACT.md).
- **Sem CORS Agressivo e Sem Mocks na API:** A comunicação web/api roda orientada a cookies de sessão `HttpOnly` com validação de cabeçalho `X-Hub-Request: 1`. Endpoints não devem mockar dados para "parecer pronto" se a regra de persistência e auditoria não existir.

## 4. Contratos de Interface entre as Apps
- **Autenticação:** Cookie HttpOnly gerado em `/api/v1/auth/login` e enviado nas requisições do cliente HTTP web; o shell verifica a sessão no cliente.
- **Contrato de Números:** A `api` serializa números decimais em strings nos payloads JSON (`"1500.50"`). O `web` as formata via [format.ts](web/src/lib/format.ts), sem recalcular saldos ou resultados financeiros com `Number`. Conversões para coordenadas SVG e validação de exibição não produzem valores financeiros canônicos.
- **Identidade vs Listagem:** O frontend referencia ativos financeiros por seus `id` imutáveis (UUID), e nunca puramente por `ticker`, pois tickers podem mudar de bolsa, sofrer renomeação ou reuso.

## 5. Roteiro por Etapas (Ao fim das etapas)

Cobertura obrigatória no [plano](../docs/IMPLEMENTATION_PLAN.md) e na [matriz](../docs/REQUIREMENTS_MATRIX.md); esta lista não declara serviços futuros disponíveis.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - `apps/api` e `apps/web` cobrindo com dados reais persistidos as 12 páginas-base (P01 Início, P02 Aprender, P03 Mercado, P04 Empresas, P08 Macro, P10 Carteiras, P11 Operações, P12 Proventos, P19 Diário, P21 Relatórios, P22 Dados, P23 Administração).
  - Implementação do servidor de relatórios (CSV, PDF) e servidor MCP inicial.
  - Um mecanismo de jobs durável, com execução, estados persistidos, retomada após reinício, retentativas limitadas e cancelamento explícito antes de aceitar tarefas em segundo plano. A pasta física do worker é uma decisão de organização, não condição para adiar essas garantias.
  - Integrar serviços e telas de S01/S02/S12/S03/S07/S21/S23: performance/metas, mercado/watchlists, fundamentos/TTM, macro, aprendizado e diário/teses/comentários básicos, com fontes, wrappers e avaliações.
  - Fontes reais, originais/snapshots versionados, CSV/XLSX com reconciliação e qualidade/quarentena; comprovar reinício, backup/restauração inicial, primeira linha de base medida e jornadas A/B/F na cobertura da etapa.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - `apps/web` e `apps/api` ampliadas para suportar as telas analíticas avançadas: P05 FIIs, P06 Renda Fixa, P07 ETFs/Globais, P09 Valuation, P13 Tributação, P14 Riscos, P15 Otimização, P16 Backtesting, P17 Radar.
  - Endpoints analíticos com histórico de premissas e versões editáveis.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Ampliar a operação do worker para ingestão contínua e inferência de IA; criar `apps/worker/` se a separação física se justificar, preservando a execução durável exigida desde a Etapa 1.
  - `apps/web` com suporte a colaboração multiusuário em tempo real, tela P18 Comitê IA e P20 Alertas/Monitoramento.
  - Conexão e sincronização perfeita entre as 23 páginas e 23 skills.

## 6. O Que Fica Fora de Escopo
- Não criar pastas `apps/worker` ou `apps/mcp` enquanto não houver código real e testes correspondentes.
- Não colocar scripts utilitários ou de setup dentro de `apps/` (esses pertencem a `scripts/`).

## 7. Verificação
- **API:** Consulte [apps/api/CONTEXT.md](api/CONTEXT.md) para os comandos de Pytest e migrações.
- **Web:** Consulte [apps/web/CONTEXT.md](web/CONTEXT.md) para typecheck, lint, testes Node via `tsx --test` e build Next.js.
