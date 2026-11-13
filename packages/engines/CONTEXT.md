# Contexto de `packages/engines` — Motor Financeiro (`hub_finance`)

## 1. Missão e Objetivo (Goal)
O `packages/engines` abriga a biblioteca Python **`hub_finance`**, que é o coração matemático e contábil do Investment Research Hub.
Sua missão é implementar a contabilidade canônica em partidas dobradas, posições, custo, caixa e resultados. Na base, `hub_finance.ledger` aplica eventos em memória; a API persiste o histórico imutável e ainda calcula avaliações/agregações em `portfolio_service.py`. API, futuros MCP/relatórios e telas devem reutilizar esses cálculos.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Código-Fonte (`src/hub_finance/`):**
  - `__init__.py`: Docstring do pacote; funções/tipos públicos são importados de `hub_finance.ledger`.
  - `ledger.py`: Método `average-cost-brl/1.0.1`, eventos Decimal e lançamentos balanceados; recebe um evento por chamada e atualiza posições por instrumento. Ordenação/replay por carteira ficam na API.
  - `py.typed`: Marcador PEP 561 de tipos distribuídos; Mypy estrito é uma verificação separada.
- [x] **Tipos de Eventos Suportados no Ledger (`EventType`):**
  - `deposit`: Aporte BRL (aumenta caixa e contribuições líquidas).
  - `withdrawal`: Retirada (reduz caixa e contribuições; rejeita saldo negativo).
  - `buy`: Compra (aumenta custódia/custo, reduz caixa incluindo taxas/tributos).
  - `sell`: Venda (reduz custódia/custo, credita o valor líquido e apura resultado; encargos acima do bruto exigem caixa suficiente).
  - `dividend`: Provento recebido (credita valor líquido, sem alterar a quantidade).
  - `fee`: Taxa operacional (reduz caixa e registra despesa).
  - `tax`: Tributo pago (reduz caixa e registra despesa; não calcula obrigação fiscal).
  - `split`: Desdobramento/grupamento (altera quantidade preservando custo total; rejeita frações não representáveis).
- [x] **Testes de Unidade e Propriedades:**
  - `tests/unit/test_ledger.py`: Casos determinísticos e propriedade Hypothesis (`@given`) de balanço/conservação.
  - `tests/unit/test_ledger_adversarial.py`: Casos determinísticos/parametrizados de frações, overflow, falhas atômicas, splits/avaliações e segregação econômica.

Fontes: [ledger.py](src/hub_finance/ledger.py), [serviço de portfólio](../../apps/api/src/hub_api/portfolio_service.py), [testes do ledger](../../tests/unit/test_ledger.py), [adversariais](../../tests/unit/test_ledger_adversarial.py) e [auditoria F05/F10/F12](../../docs/CONTEXT_PLAN_COMPARISON.md).

## 3. Contrato Local: Inputs, Process e Outputs

### Inputs (Entradas e o que ler)
- **Leitura obrigatória antes de editar:** [docs/COMPUTE_ARCHITECTURE.md](../../docs/COMPUTE_ARCHITECTURE.md) e o histórico de revisões contábeis em `tests/unit/test_ledger.py`.
- **Tipos de Entrada:** `apply_event(state: LedgerState, event: Event)` recebe estado mutável e evento `@dataclass(frozen=True)` com `event_type` minúsculo, `trade_date: date`, `instrument_id: str | None` e campos `Decimal`.
- **Isolamento:** Proibido receber modelos SQLAlchemy, dicionários JSON crus de requisição ou tipos ORM.

### Process (Fluxo e como trabalhar)
1. Para adicionar ou modificar operações contábeis ou financeiras:
   - Manter determinismo e ausência de I/O. `apply_event` valida antes de modificar o estado; `LedgerState` e `Position` são mutáveis, `Event` e `Posting` são congelados.
   - Não consultar relógio do sistema. `trade_date` vem no evento; ordenação e corte `as_of` pertencem ao serviço de replay/consulta, não a um parâmetro já existente de `apply_event`.
   - Preservar contexto Decimal de precisão 50, caixa BRL em centavos com `ROUND_HALF_EVEN` e custo alocado de venda parcial em 16 casas; venda final consome o custo remanescente exato.
2. Para adicionar novos motores analíticos (renda fixa, valuation, risco):
   - Criar submódulos dedicados em `src/hub_finance/` (ex: `fixed_income.py`, `risk.py`).
   - Adicionar tipagem estrita com checagem Mypy limpa.
   - Criar testes unitários com valores analíticos conhecidos de mercado antes de disponibilizar para a API.

### Outputs (Entregas e saídas esperadas)
- Contrato público atual:
  ```python
  def apply_event(state: LedgerState, event: Event) -> list[Posting]: ...
  ```
  Retorna lançamentos balanceados e atualiza o estado recebido. `LedgerState` contém `cash`, `net_contributions`, `income`, `realized_pnl`, `expenses`, `positions: dict[str, Position]` e a propriedade calculada `total_cost`; `Position` contém `quantity`/`cost_basis`.
- Violações de domínio lançam `LedgerError(ValueError)` antes da mutação; a API o converte para HTTP 422/`INVALID_EVENT`. Não existem `PortfolioState`, `InsufficientCashError` ou `InsufficientPositionError` nessa base.

## 4. Regras de Negócio e Invariantes Locais (Layer 5)
- **Precisão Decimal Rígida:** O ledger e o dinheiro canônico não usam `float`. Quantidades/preços de entrada admitem até 8 casas, taxas/tributos/caixa BRL em centavos; derivados científicos futuros podem usar float64 com tolerâncias explícitas, conforme Promptx §5.5 e a arquitetura computacional.
- **Não-Negatividade de Ativos e Caixa:** O motor rejeita venda acima da posição e caixa negativo após o evento. A base reconhece caixa por negociação; `settlement_date` é informativa na API e não representa saldo liquidado disponível para saque.
- **Conservação de Custo no Split:** Desdobramentos e grupamentos ajustam a quantidade de quotas e o custo unitário de forma que $\text{Quantidade Final} \times \text{Custo Unitário Final} = \text{Custo Total Original}$. O split não movimenta caixa nem altera resultados já realizados.
- **Imutabilidade e Idempotência:** O estado de trabalho é mutável. Histórico append-only é garantido pela [migração](../../apps/api/migrations/versions/0002_ledger_integrity.py); idempotência/locks ficam na API e no banco. Chamar `apply_event` duas vezes aplica o evento duas vezes: o motor não deduplica nem persiste snapshots.

## 5. Roteiro por Etapas (Ao fim das etapas)

Cobertura exigida pelo [plano](../../docs/IMPLEMENTATION_PLAN.md) e pelo [catálogo T01–T56](../../docs/REQUIREMENTS_MATRIX.md); nomes de módulos futuros não representam código disponível.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Suporte a eventos de transferência interna entre carteiras e contas.
  - Suporte a conversão cambial multi-moedas em transações de ativos internacionais.
  - Cálculo formal de métricas de rentabilidade temporal canônica: TWR (Time-Weighted Return) e MWR/TIR (Money-Weighted Return).
  - Casos T01–T07 na cobertura da etapa com testes de unidade e integração apropriados: T04/T05 exigem reprocessamento/arquivos, T06 transferências e T07 segregação fiscal por titular (apuração S16 completa na Etapa 2).
  - T15: split/grupamento preserva patrimônio, emissão com aporte tem efeitos próprios; T21: não duplicar provento em série ajustada e caixa; T25: anunciado/cancelado/recebido distintos; T26: retorno em moeda-base com câmbio e datas coerentes.
  - S01/S12: saldos iniciais, amortizações/proventos, correções versionadas e reconciliação, qualidade/unidades/períodos/nulos e disponibilidade histórica (T08–T12), com autoria/persistência controladas pelos serviços.
  - Cálculos canônicos de S02 (séries/comparações), S03 (fundamentos/TTM/setores), S07 (macro) e metas; S23 usa os mesmos cálculos em exemplos executados e S21 exporta seus resultados com fontes/versões.
  - Manifesto dos motores e primeira linha de base medida na Etapa 1 em `docs/PERFORMANCE_BASELINE.md`, separando motor, preparação, banco e consulta completa.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Expansão dos submódulos do motor financeiro:
    - `hub_finance.fixed_income`: Precificação de títulos prefixados, IPCA+ e pós-fixados (% CDI) com base em curvas de juros e dias úteis (calendário ANBIMA).
    - `hub_finance.valuation`: Modelagem de fluxo de caixa descontado (DCF), valor terminal (Gordon Shapiro) e custo de capital (WACC).
    - `hub_finance.risk`: Matriz de covariância, VaR paramétrico e histórico, Expected Shortfall (CVaR) e drawdowns.
    - `hub_finance.simulations`: Motor Monte Carlo reutilizável com gerador pseudoaleatório determinístico (seed fixável).
    - `hub_finance.optimization`: Algoritmos de otimização de carteiras (Markowitz, paridade de risco) com restrições de lotes e custos.
    - `hub_finance.backtest`: Execução de estratégias em séries temporais com proibição estrita de *look-ahead bias*.
    - `hub_finance.tax`: Apuração mensal, isenções, compensação de prejuízos e demonstrativos/DARFs individuais, condicionados à verificação de fonte oficial, jurisdição/categoria, titular e vigência; nenhum limite/alíquota citado informalmente é regra validada, nem há transmissão/pagamento automáticos.
  - Ampliar e comparar a linha de base iniciada na Etapa 1 em `docs/PERFORMANCE_BASELINE.md` antes de adotar Rust/Julia; equivalência segue a política numérica, sem identidade binária universal.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Módulos de reconciliação de direitos de subscrição, bonificações e cancelamentos oficiais emitidos pela B3/CVM.
  - Algoritmos determinísticos de detecção de anomalias de preços e dividendos para alimentar o sistema de alertas.

## 6. O Que Fica Fora de Escopo
- Nenhuma operação de I/O em disco, rede ou banco de dados dentro de `hub_finance`.
- Nenhuma dependência de bibliotecas web (FastAPI, Starlette, Pydantic, etc.).
- Proibido o uso de `datetime.now()` ou relógios do sistema dentro dos cálculos; o tempo de cálculo deve ser passado explicitamente via parâmetro `as_of`.

## 7. Verificação e Comandos
- **Testes Unitários, Propriedade Hypothesis e Casos Adversariais (a partir da raiz):**
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
