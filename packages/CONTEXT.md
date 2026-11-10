# Contexto de `packages/` — Pacotes Compartilhados da Aplicação

## 1. Missão e Objetivo (Goal)
O diretório `packages/` contém bibliotecas internas e motores computacionais reutilizáveis que não possuem ciclo de vida como processo servidor autônomo.
Sua missão é centralizar a lógica de negócios, cálculos matemáticos, regras contábeis e modelos de domínio para que sejam consumidos de forma idêntica e sem duplicidade por qualquer aplicação em `apps/` (API REST, ferramentas de linha de comando, servidores MCP ou futuros scripts analíticos).

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] [`engines/`](engines/CONTEXT.md) — Pacote Python `hub_finance`: O motor financeiro institucional com contabilidade em partidas dobradas, precisão `Decimal` e gerenciamento de posições.

## 3. Regras de Negócio e Invariantes Locais
- **Aceleração Condicional e Evidência (Rust/Julia):**
  - Conforme definido em [docs/COMPUTE_ARCHITECTURE.md](../docs/COMPUTE_ARCHITECTURE.md), toda lógica financeira começa e tem como especificação primária o motor em Python com `Decimal`.
  - Módulos em Rust ou Julia só podem ser criados na Etapa 2 e após comprovação prévia de benefício real de performance em benchmark registrado e validação formal de equivalência numérica bit-a-bit.
  - Proibido criar pastas de crates Rust ou scripts Julia vazios apenas para "demonstrar intenção arquitetural".
- **Independência de Protocolo:**
  - Código dentro de `packages/` é puro e livre de protocolos HTTP, frameworks de apresentação (FastAPI, Next.js) e acesso direto a bancos de dados externos.
  - Recebe dados em memória (estruturas de dados puras, tipos primitivos ou dataclasses) e devolve resultados determinísticos.

## 4. Contratos de Interface com Outros Módulos
- Aplicações em `apps/api` instalam `hub_finance` em modo editável (`pip install -e packages/engines`) gerenciado pelo arquivo `pyproject.toml` da raiz.
- As funções públicas devem ser tipadas e verificadas via `mypy` com o marcador `py.typed`.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Consolidação e teste exaustivo do pacote `hub_finance` para suportar: eventos contábeis completos, cálculo canônico de preço médio ponderado, apuração de resultado realizado/não realizado, splits e amortizações sem perda de centavos.
  - Testes de concorrência e propriedades com Hypothesis.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Adição de novos submódulos matemáticos dentro de `engines/` (ou novos pacotes caso justificado):
    - Motor de Renda Fixa (curvas de juros, marcação a mercado, duration).
    - Motor de Valuation (Fluxo de Caixa Descontado, Dividend Discount Model).
    - Motor de Risco e Monte Carlo (VaR, CVaR, simulações de trajetória com RNG determinístico).
    - Motor de Otimização e Fronteira Eficiente (Markowitz, Black-Litterman, rebalanceamento por lotes).
    - Motor de Backtesting e Sinais Temporais (sem vazamento de dados futuros / look-ahead bias).
  - Avaliação de necessidade de aceleração em Rust para Monte Carlo / Otimização combinatória com documentação em `docs/PERFORMANCE_BASELINE.md`.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Algoritmos determinísticos de detecção de anomalias econômicas e divergências de dados oficiais de bolsa.

## 6. O Que Fica Fora de Escopo
- Não colocar lógica de controle de sessão, tokens JWT ou senhas em `packages/`.
- Não conectar banco de dados (PostgreSQL/SQLAlchemy) diretamente dentro de `packages/engines`.
- Não criar pastas fictícias ou esqueletos de código sem testes reais associados.

## 7. Verificação
Consulte [packages/engines/CONTEXT.md](engines/CONTEXT.md) para os comandos de execução dos testes de unidade com Pytest e checagem de tipos estrita.
