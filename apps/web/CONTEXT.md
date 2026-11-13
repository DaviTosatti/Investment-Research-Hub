# Contexto de `apps/web` — Interface do Usuário (Next.js)

## 1. Missão e Objetivo (Goal)
O `apps/web` provê a interface do usuário do Investment Research Hub construída com Next.js 16.4.5 (App Router), React 19.3.1, TypeScript e CSS próprio em `src/app/globals.css`.
Sua missão é entregar uma experiência visual profissional com **identidade fintech escura** (inspirada nas referências aprovadas em `docs/VISUAL_REFERENCES.md`), acessibilidade, responsividade para desktop e dispositivos móveis, e consumo da API `/api/v1` sem recalcular valores financeiros canônicos no navegador. Coordenadas SVG usam `Number` apenas para desenho.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Importação integrada:** `import-workspace.tsx`, `import-config.ts` e `import-types.ts` implementam o fluxo de [IMPORTS.md](../../docs/IMPORTS.md) em `/dados#importacoes`, ligado por `/operacoes`. Paginação, histórico após recarregar, alterações justificadas, decisões, revisão obsoleta/somente leitura e permissões usam os contratos reais. Valores são calculados pela API.
- [x] **Páginas e Rotas Implementadas (`src/app/`):**
  - Rota Raiz: `/` redireciona para `/inicio`; o shell do Hub verifica a sessão e encaminha ao `/login` quando necessário.
  - Rotas Autenticadas do Hub (`(hub)/`):
    - `inicio/page.tsx` (P01): Visão consolidada de patrimônio, alocação, caixa e posições.
    - `carteiras/page.tsx` (P10): Cadastro de titulares, carteiras/contas, tabela de carteiras e link para posições no Início.
    - `operacoes/page.tsx` (P11): Cadastro de ativos e registro/listagem de transações (aporte, retirada, compra, venda, dividendos, taxas, tributos, splits).
    - `dados/page.tsx` (P22): Importação guiada CSV/XLSX, originais, prévias, correções, reconciliação, confirmação e recibos; avaliações manuais, cobertura das avaliações e trilha de ações do grupo.
    - `administracao/page.tsx` (P23): Cadastro/listagem de membros e apresentação dos papéis de acesso.
  - Tratamento de Falhas: `error.tsx` e `not-found.tsx`.
- [x] **Componentes do Design System (`src/components/`):**
  - `hub-shell.tsx`: Navegação, sessão, idioma, filtros de titular/carteira/data e atualização manual; não há indicador de saúde.
  - `positions-table.tsx`: Renderiza todas as posições recebidas, com quantidade, custo, cotação e resultado; sem paginação própria.
  - `allocation-chart.tsx`: Gráfico SVG de alocação por classe de ativos sem dependências pesadas externas.
  - `history-chart.tsx`: Histórico de patrimônio a custo e aportes líquidos; não representa rentabilidade nem série de valor de mercado.
  - `manual-price-form.tsx`: Formulário com validação local de preço e data.
  - `snapshot-export.tsx`: Botão e controle de download de relatório CSV.
  - `ui.tsx`: Ícones, cabeçalhos, painéis, campos, botão de submissão, avisos, badges de qualidade, paginação e estados de carregamento/erro/vazio; sem biblioteca genérica de modais.
- [x] **Bibliotecas Utilitárias e Integrações (`src/lib/`):**
  - `api.ts`: Cliente HTTP com suporte a cookie de sessão, injeção de `X-Hub-Request` e tratamento de erros institucionais.
  - `format.ts`: Formatação de moeda brasileira (BRL), porcentagens e datas com fuso horário `America/Sao_Paulo`.
  - `forms.ts`: Normalização decimal e payload de transação; `idempotentRequest` recebe um gerador de chave e reutiliza a chave para payload inalterado após resultado de rede incerto.
  - `types.ts`: Contratos TypeScript espelhando fielmente os schemas da API.
  - `use-resource.ts`: Hook de requisição por chave/dependência, com cancelamento, descarte de resposta obsoleta e estado de carregamento/erro; sem polling periódico ou cache de consultas reutilizável.
- [x] **Testes Automatizados (`tests/`):**
  - 40 testes no incremento E1.21 via `tsx --test tests/*.test.ts` (Node): contratos HTTP, formatação, formulários e renderização de gráficos (`api.test.ts`, `charts.test.ts`, `format.test.ts`, `forms.test.ts`). Os testes unitários não substituem jornadas no navegador; E1.21 também validou o fluxo de importação em Chromium com banco sintético, sem representar homologação completa do produto.

Fontes: [package.json](package.json), [páginas do Hub](<src/app/(hub)>), [shell](src/components/hub-shell.tsx), [tabela de posições](src/components/positions-table.tsx), [UI](src/components/ui.tsx), [hook](src/lib/use-resource.ts), [formatadores](src/lib/format.ts), [formulários](src/lib/forms.ts) e [auditoria F06/F07](../../docs/CONTEXT_PLAN_COMPARISON.md). São cinco páginas-base parciais. Importação e snapshots recuperáveis de prévias estão entregues no recorte de operações; provedores externos, snapshots de análises e performance permanecem pendentes.

## 3. Contrato Local: Inputs, Process e Outputs

### Inputs (Entradas e o que ler)
- **Leitura obrigatória antes de editar:** [docs/VISUAL_REFERENCES.md](../../docs/VISUAL_REFERENCES.md) para componentes visuais e paleta; [docs/API_CONTRACT.md](../../docs/API_CONTRACT.md) para tipos de payloads.
- **Tipos de dados:** Schemas TypeScript em `src/lib/types.ts`.
- **Payloads recebidos da API:** Todas as quantias e preços chegam como strings (`"1500.50"`).

### Process (Fluxo e como trabalhar)
1. Para criar ou alterar páginas/componentes:
   - Utilizar componentes base de `src/components/ui.tsx` e classes/tokens de `src/app/globals.css`, respeitando o tema fintech escuro.
   - Tratar estados de carregamento (`loading`), erro (`error`) e estado vazio (`empty state`).
2. Para manipulação de valores financeiros:
   - Proibido converter strings monetárias para `Number` para calcular totais.
   - Passar strings para `money`, `unitPrice`, `number`, `percent` e datas para `date` em `src/lib/format.ts`; os valores formatados preservam as strings decimais exatas.
3. Para formulários de mutação:
   - Para transações, usar `idempotentRequest` com `crypto.randomUUID`; reutilizar a chave apenas para payload inalterado após resposta incerta, trocando-a quando o payload mudar ou a operação anterior for confirmada.
   - Enviar requisições pelo cliente `src/lib/api.ts` (garante envio automático do header `X-Hub-Request: 1`).

### Outputs (Entregas e saídas esperadas)
- Critérios a validar: acessibilidade WCAG AA, teclado/foco/contraste e layout em 1440/1024/768/390 px (Promptx §2; matriz T42/T43). Larguras 1920/375 px podem complementar. Referências aprovadas não equivalem a homologação das telas.
- Testes relevantes em `tests/` com `node:test` via `tsx --test`; não há Vitest nas dependências.
- Executar typecheck, lint, testes e build separadamente conforme `package.json`; build sozinho não comprova ESLint nem QA visual.

## 4. Regras de Negócio e Invariantes Locais (Layer 5)
- **Proibição de Float para Cálculos:** O frontend não recalcula saldos, ganhos de capital ou TWR usando `Number` do JavaScript. Todos os totais vêm calculados da API e são tratados como strings para exibição via `format.ts`.
- **Identidade Fintech Escura:** Cores e contrastes devem respeitar estritamente o tema fintech escuro documentado em [docs/VISUAL_REFERENCES.md](../../docs/VISUAL_REFERENCES.md). Dashboards no padrão claro de adquirência são vetados.
- **Idempotência no Cliente:** O guard de submissão impede cliques concorrentes; `idempotentRequest` conserva a chave quando se reenvia a mesma intenção incerta. Gerar outra chave a cada retry pode duplicar o fato.
- **Acessibilidade e Semântica:** Elementos visuais devem possuir atributos ARIA, labels em inputs, e contraste acessível em conformidade com WCAG AA.
- **Distinção de Titularidade:** Consultas são compartilhadas; os filtros selecionam titular/carteira ou consolidado do grupo, padrão inicial do shell. Preservar identificação individual nas posições/operações; consolidar não transforma patrimônios em conta ou contribuinte único.

## 5. Roteiro por Etapas (Ao fim das etapas)

Rotas futuras seguem os contratos da [matriz](../../docs/REQUIREMENTS_MATRIX.md) e do [plano](../../docs/IMPLEMENTATION_PLAN.md); não são páginas existentes.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Completar a cobertura das 12 páginas-base previstas:
    - P02 `/aprender` (Trilhas didáticas e glossário do Mentor S23).
    - P03 `/mercado` (Watchlists e cotações de mercado S02).
    - P04 `/empresas/:instrument_id` (Fundamentos e múltiplos TTM S03; rota proposta na matriz).
    - P08 `/macroeconomia` (Selic, IPCA, câmbio e juros externos S07).
    - P12 `/proventos` (Dividendos anunciados, recebidos e projetados).
    - P19 `/diario` (Diário de bordo e teses de investimento).
    - P21 `/relatorios` (Geração e download de relatórios em múltiplos formatos).
  - Upload CSV/XLSX com mapeamento, prévia, confirmação, reconciliação de duplicatas entre arquivos e correção rastreável, preservando original e decisões; exibir erros/quarentena sem fabricar dados.
  - Metas e performance canônica em carteiras/dashboard, proveniência e disponibilidade dos dados, teses/comentários com versões e exemplos didáticos executados; relatórios com os mesmos filtros/snapshot.
  - Acompanhamento de jobs duráveis com retomada após reload, progresso/falhas e cancelamento explícito; desconectar a página não cancela trabalho aceito.
  - Revisão visual nas quatro larguras e jornadas A/recortes B/F com dois usuários, dados/preferências preservados após reinício e evidência da primeira linha de base de interface/serviços.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Construção das 9 páginas analíticas avançadas:
    - P05 `/explorar/fiis`, P06 `/explorar/renda-fixa`, P07 `/explorar/globais`.
    - P09 `/valuation` (Editor de fluxo de caixa descontado e múltiplos).
    - P13 `/tributacao` (Demonstrativo e simulações fiscais individuais).
    - P14 `/riscos` (Gráficos de estresse, drawdown e simulação de Monte Carlo).
    - P15 `/estrategias/otimizacao` (Fronteira eficiente e rebalanceamento).
    - P16 `/estrategias/backtesting` (Visualizador de curvas e trades passados).
    - P17 `/radar` (Screener quantitativo e qualitativo de oportunidades).
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - P18 `/comite` (Interface para debater teses com especialistas IA e síntese de deliberação).
  - P20 `/monitoramento` (Central de alertas, notificações e agendamento de rotinas).
  - Colaboração com controle de concorrência e presença de múltiplos usuários editando teses.

## 6. O Que Fica Fora de Escopo
- Não simular gráficos ou métricas financeiras complexas usando mocks de tela quando a API ainda não possuir o motor correspondente.
- Não introduzir bibliotecas de componentes pesadas (ex: MUI, Chakra, AntDesign); reutilizar os componentes React e o CSS próprio do Hub.
- Nenhuma funcionalidade de trading direto ou integração de home-broker.

## 7. Verificação e Comandos
Dentro da pasta `apps/web`:
- **Checagem de Tipos TypeScript:**
  ```bash
  npm run typecheck
  ```
- **Linter:**
  ```bash
  npm run lint
  ```
- **Testes Unitários:**
  ```bash
  npm run test
  ```
- **Build de Produção:**
  ```bash
  npm run build
  ```
