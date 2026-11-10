# Contexto de `apps/web` — Interface do Usuário (Next.js)

## 1. Missão e Objetivo (Goal)
O `apps/web` provê a interface do usuário do Investment Research Hub construída com Next.js 15 (App Router), TypeScript e Tailwind CSS.
Sua missão é entregar uma experiência visual profissional com **identidade fintech escura** (inspirada nas referências aprovadas em `docs/VISUAL_REFERENCES.md`), garantindo acessibilidade, responsividade para desktop e dispositivos móveis, e consumo estrito da API `/api/v1` sem realizar operações matemáticas com números de ponto flutuante.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Páginas e Rotas Implementadas (`src/app/`):**
  - Rota Raiz: `/` (redirecionamento autenticado) e `/login` (autenticação com sessão segura).
  - Rotas Autenticadas do Hub (`(hub)/`):
    - `inicio/page.tsx` (P01): Visão consolidada de patrimônio, alocação, caixa e posições.
    - `carteiras/page.tsx` (P10): Gestão de carteiras, seleção por titular econômico, tabela de posições.
    - `operacoes/page.tsx` (P11): Registro de transações (aporte, retirada, compra, venda, dividendos, splits).
    - `dados/page.tsx` (P22): Gestão e cadastro de cotações manuais.
    - `administracao/page.tsx` (P23): Cadastro de membros, titulares econômicos, ativos e visualização de trilha de auditoria.
  - Tratamento de Falhas: `error.tsx` e `not-found.tsx`.
- [x] **Componentes do Design System (`src/components/`):**
  - `hub-shell.tsx`: Layout principal com barra de navegação, status da sessão, seletor de titular e indicador de saúde.
  - `positions-table.tsx`: Tabela com paginação, colunas de quantidade, custo, cotação e resultado.
  - `allocation-chart.tsx`: Gráfico SVG de alocação por classe de ativos sem dependências pesadas externas.
  - `history-chart.tsx`: Gráfico de evolução temporal e patrimonial.
  - `manual-price-form.tsx`: Formulário com validação local de preço e data.
  - `snapshot-export.tsx`: Botão e controle de download de relatório CSV.
  - `ui.tsx`: Botões, inputs, cards, modais e badges seguindo o tema fintech escuro.
- [x] **Bibliotecas Utilitárias e Integrações (`src/lib/`):**
  - `api.ts`: Cliente HTTP com suporte a cookie de sessão, injeção de `X-Hub-Request` e tratamento de erros institucionais.
  - `format.ts`: Formatação de moeda brasileira (BRL), porcentagens e datas com fuso horário `America/Sao_Paulo`.
  - `forms.ts`: Geração e controle de chaves de idempotência para submissão de formulários.
  - `types.ts`: Contratos TypeScript espelhando fielmente os schemas da API.
  - `use-resource.ts`: Hook React para polling controlado, cache em memória e estado de carregamento/erro.
- [x] **Testes Automatizados (`tests/`):**
  - 24 testes unitários e de integração de componentes (`api.test.ts`, `charts.test.ts`, `format.test.ts`, `forms.test.ts`).

## 3. Regras de Negócio e Invariantes Locais
- **Proibição de Float para Cálculos:** O frontend não recalcula saldos, ganhos de capital ou TWR usando `Number` do JavaScript. Todos os totais vêm calculados da API e são tratados como strings para exibição via `format.ts`.
- **Identidade Fintech Escura:** Cores e contrastes devem respeitar estritamente o tema fintech escuro documentado em [docs/VISUAL_REFERENCES.md](../../docs/VISUAL_REFERENCES.md). Dashboards no padrão claro de adquirência são vetados.
- **Idempotência no Cliente:** Qualquer submissão de transação deve gerar uma chave única UUID via `forms.ts` para evitar duplicatas em cliques duplos ou reenvios de rede.
- **Acessibilidade e Semântica:** Elementos visuais devem possuir atributos ARIA, labels em inputs, e contraste acessível em conformidade com WCAG AA.
- **Distinção de Titularidade:** Nunca misturar patrimônio de titulares econômicos distintos a menos que o filtro "Grupo Consolidado" esteja expressamente selecionado.

## 4. Contratos de Interface (Consumo da API)
- O frontend consome exclusivamente a base `/api/v1`.
- Respostas paginadas utilizam a interface:
  ```typescript
  interface Page<T> {
    items: T[];
    total: number;
    limit: number;
    offset: number;
  }
  ```
- Erros de API exibem a mensagem original mapeada de `ApiError` sem quebrar o layout da página.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Completar a cobertura das 12 páginas-base previstas:
    - P02 `/aprender` (Trilhas didáticas e glossário do Mentor S23).
    - P03 `/mercado` (Watchlists e cotações de mercado S02).
    - P04 `/acoes` (Análise de fundamentos e múltiplos TTM S03).
    - P08 `/macroeconomia` (Selic, IPCA, câmbio e juros externos S07).
    - P12 `/proventos` (Dividendos anunciados, recebidos e projetados).
    - P19 `/diario` (Diário de bordo e teses de investimento).
    - P21 `/relatorios` (Geração e download de relatórios em múltiplos formatos).
  - Implementação de upload de arquivos CSV/XLSX com interface de mapeamento de colunas e pré-visualização.
  - Revisão visual responsiva para celular em todas as 12 páginas.
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
- Não introduzir bibliotecas de componentes pesadas (ex: MUI, Chakra, AntDesign); utilizar os componentes nativos Tailwind do Hub.
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
