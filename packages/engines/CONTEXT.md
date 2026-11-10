# Contexto de `packages/engines` — Motor Financeiro (`hub_finance`)

## 1. Missão e Objetivo (Goal)
O `packages/engines` abriga a biblioteca Python **`hub_finance`**, que é o coração matemático e contábil do Investment Research Hub.
Sua missão é implementar a lógica canônica de contabilidade em partidas dobradas, registro de eventos imutáveis, cálculo de posições em custódia, preço médio, saldo em caixa e apuração de resultados financeiros. Ele atua como **fonte única da verdade de cálculo** para a API, MCP, relatórios e telas do sistema.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Código-Fonte (`src/hub_finance/`):**
  - `__init__.py`: Exportações canônicas do pacote.
  - `ledger.py`: Motor de eventos contábeis implementado inteiramente com tipos `Decimal`, suporte a partidas dobradas (débito/crédito), processamento temporal de transações e agregação de posições por carteira/ativo.
  - `py.typed`: Arquivo marcador informando conformidade estrita com PEP 561 (verificação por Mypy).
- [x] **Tipos de Eventos Suportados no Ledger (`EventType`):**
  - `DEPOSIT`: Aporte em moeda corrente (aumenta caixa da carteira).
  - `WITHDRAWAL`: Retirada de caixa (reduz caixa; rejeita saldo negativo).
  - `BUY`: Compra de ativo (aumenta custódia, reduz caixa considerando taxas/emolumentos e recalcula preço médio).
  - `SELL`: Venda de ativo (reduz custódia, aumenta caixa, apura ganho/perda de capital realizado).
  - `DIVIDEND`: Provento em dinheiro (aumenta caixa, não altera quantidade de ativos em custódia).
  - `FEE`: Taxa operacional ou corretagem (reduz caixa).
  - `TAX`: Recolhimento de tributo/imposto (reduz caixa).
  - `SPLIT`: Desdobramento ou grupamento de ações (altera quantidade de cotas mantendo o custo de aquisição total inalterado).
- [x] **Testes de Unidade e Propriedades:**
  - `tests/unit/test_ledger.py`: Casos de teste determinísticos cobrindo regras contábeis normativas.
  - `tests/unit/test_ledger_adversarial.py`: Testes com geração aleatória de propriedades via `Hypothesis` validando conservação de valor e robustez sob ordens extremas de eventos.

## 3. Regras de Negócio e Invariantes Locais (Invariantes Financeiras)
- **Precisão Decimal Rígida:**
  - É expressamente proibido o uso de `float` em qualquer ponto do motor financeiro.
  - Todas as quantidades, cotações, saldos e valores monetários devem ser instâncias de `decimal.Decimal`.
  - Divisões utilizam políticas de arredondamento canônicas explícitas (`ROUND_HALF_UP` ou `ROUND_HALF_EVEN`), preservando centavos.
- **Não-Negatividade de Ativos e Caixa:**
  - O motor rejeita vendas de ativos a descoberto (`short selling`) neste estágio. Se a quantidade vendida exceder a custódia disponível na data do trade, o motor lança erro de domínio.
  - A conta corrente associada à carteira não pode ficar com saldo negativo após a liquidação do evento.
- **Conservação de Custo no Split:**
  - Desdobramentos (`split` com fator > 1) e grupamentos (`split` com fator < 1) ajustam a quantidade de quotas e o custo unitário de forma que:
    $$\text{Quantidade Final} \times \text{Custo Unitário Final} = \text{Custo Total Original}$$
  - O split não movimenta caixa nem altera resultados já realizados.
- **Imutabilidade e Idempotência:**
  - Funções de processamento de ledger são puras: recebem uma lista de eventos e retornam um snapshot de posições e caixa sem efeitos colaterais.

## 4. Contratos de Interface (Inputs, Process, Outputs)
- **Entrada Principal:**
  ```python
  class LedgerEvent:
      event_type: EventType
      event_date: date
      instrument_id: UUID | None
      quantity: Decimal | None
      unit_price: Decimal | None
      gross_amount: Decimal
      fees: Decimal = Decimal("0")
      taxes: Decimal = Decimal("0")
  ```
- **Saída:**
  ```python
  class PortfolioState:
      cash: Decimal
      total_cost: Decimal
      positions: dict[UUID, Position]
      realized_pnl: Decimal
  ```

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Suporte a eventos de transferência interna entre carteiras e contas.
  - Suporte a conversão cambial multi-moedas em transações de ativos internacionais.
  - Cálculo formal de métricas de rentabilidade temporal canônica: TWR (Time-Weighted Return) e MWR/TIR (Money-Weighted Return).
  - Casos normativos da matriz de requisitos: T01 a T07, T15, T21, T25 e T26 validados e cobertos por testes unitários.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Expansão dos submódulos do motor financeiro:
    - `hub_finance.fixed_income`: Precificação de títulos prefixados, IPCA+ e pós-fixados (% CDI) com base em curvas de juros e dias úteis (calendário ANBIMA).
    - `hub_finance.valuation`: Modelagem de fluxo de caixa descontado (DCF), valor terminal (Gordon Shapiro) e custo de capital (WACC).
    - `hub_finance.risk`: Matriz de covariância, VaR paramétrico e histórico, Expected Shortfall (CVaR) e drawdowns.
    - `hub_finance.simulations`: Motor Monte Carlo reutilizável com gerador pseudoaleatório determinístico (seed fixável).
    - `hub_finance.optimization`: Algoritmos de otimização de carteiras (Markowitz, paridade de risco) com restrições de lotes e custos.
    - `hub_finance.backtest`: Execução de estratégias em séries temporais com proibição estrita de *look-ahead bias*.
    - `hub_finance.tax`: Módulo de apuração tributária mensal com regras de isenção (R$ 20k ações), compensação de prejuízos e DARFs individuais.
  - Medição e documentação de benchmarks em `docs/PERFORMANCE_BASELINE.md` antes de considerar módulos Rust.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Módulos de reconciliação de direitos de subscrição, bonificações e cancelamentos oficiais emitidos pela B3/CVM.
  - Algoritmos determinísticos de detecção de anomalias de preços e dividendos para alimentar o sistema de alertas.

## 6. O Que Fica Fora de Escopo
- Nenhuma operação de I/O em disco, rede ou banco de dados dentro de `hub_finance`.
- Nenhuma dependência de bibliotecas web (FastAPI, Starlette, Pydantic, etc.).
- Proibido o uso de `datetime.now()` ou relógios do sistema dentro dos cálculos; o tempo de cálculo deve ser passado explicitamente via parâmetro `as_of`.

## 7. Verificação e Comandos
- **Testes Unitários e Testes Adversariais Hypothesis:**
  ```bash
  pytest tests/unit/test_ledger.py tests/unit/test_ledger_adversarial.py -v
  ```
- **Checagem Estática de Tipos com Mypy:**
  ```bash
  mypy packages/engines/src
  ```
- **Linter de Código:**
  ```bash
  ruff check packages/engines/src
  ```
