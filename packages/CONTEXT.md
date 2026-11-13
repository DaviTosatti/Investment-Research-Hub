# Contexto de `packages/` — Pacotes Compartilhados da Aplicação

## 1. Missão e Objetivo (Goal)
O diretório `packages/` contém bibliotecas internas e motores computacionais reutilizáveis que não possuem ciclo de vida como processo servidor autônomo.
Sua missão é centralizar a lógica de negócios, cálculos matemáticos, regras contábeis e modelos de domínio para que sejam consumidos de forma idêntica e sem duplicidade por qualquer aplicação em `apps/` (API REST, ferramentas de linha de comando, servidores MCP ou futuros scripts analíticos).

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] [`engines/`](engines/CONTEXT.md) — Pacote Python `hub_finance`: ledger inicial de custo médio BRL, partidas dobradas, precisão `Decimal` e posições; a cobertura completa das skills permanece pendente.

## 3. Regras de Negócio e Invariantes Locais
- **Aceleração Condicional e Evidência (Rust/Julia):**
  - Conforme [docs/COMPUTE_ARCHITECTURE.md](../docs/COMPUTE_ARCHITECTURE.md) e Promptx §5.5, Python é a interface de referência; dinheiro canônico usa `Decimal`/`NUMERIC`, enquanto matrizes/derivadas científicas podem usar float64 com tolerâncias justificadas e versionadas.
  - O roteiro da Etapa 2 avalia Rust/Julia após medir a base e as bibliotecas adequadas. Adoção exige benefício útil, equivalência de domínio/unidades/nulos/erros e política numérica, além de distribuição validada. Não há requisito universal de identidade bit a bit entre runtimes, solvers ou execuções estocásticas.
  - Proibido criar pastas de crates Rust ou scripts Julia vazios apenas para "demonstrar intenção arquitetural".
- **Independência de Protocolo:**
  - O ledger existente é livre de I/O, HTTP, frameworks de apresentação e acesso a banco. Não confundir ausência de I/O com imutabilidade: `apply_event` modifica o `LedgerState` recebido após validar o evento.
  - Recebe dados em memória (tipos primitivos/dataclasses) e produz resultados determinísticos; serviços persistem e controlam concorrência/idempotência.

## 4. Contratos de Interface com Outros Módulos
- Instalar a partir da raiz com `uv sync --locked`, conforme [bootstrap.sh](../scripts/bootstrap.sh). O [pyproject.toml](../pyproject.toml) raiz empacota `hub_api` e `hub_finance`; não existe manifesto de instalação em `packages/engines`.
- As funções públicas devem ser tipadas. `py.typed` sinaliza tipos distribuídos (PEP 561); a verificação estrita é executada pelo Mypy configurado para `hub_finance`.
- Contrato efetivo: [ledger.py](engines/src/hub_finance/ledger.py); avaliações e agregações adicionais ainda estão em [portfolio_service.py](../apps/api/src/hub_api/portfolio_service.py) e devem ser reutilizadas pelos canais consumidores.

## 5. Roteiro por Etapas (Ao fim das etapas)

Compromissos do [plano](../docs/IMPLEMENTATION_PLAN.md) e da [matriz](../docs/REQUIREMENTS_MATRIX.md); novos módulos abaixo são previstos, não pacotes já disponíveis.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Consolidação e teste exaustivo do pacote `hub_finance` para suportar: eventos contábeis completos, cálculo canônico de preço médio ponderado, apuração de resultado realizado/não realizado, splits e amortizações sem perda de centavos.
  - Testes de concorrência e propriedades com Hypothesis.
  - S01: saldos iniciais, transferências/câmbio, proventos, performance TWR/MWR (ou aproximação identificada) e metas; concorrência de gravação é validada na camada de serviço/PostgreSQL.
  - S02/S12: transformações canônicas de séries de mercado e auditoria/qualidade de dados, com identidade, unidades, períodos, nulos, versões e cutoff de disponibilidade; coleta/persistência ficam fora do ledger.
  - S03/S07: fundamentos/TTM e métricas adequadas ao setor, séries macro com frequência/unidades e observado versus hipótese explícitos.
  - S23/S21: exemplos de aprendizado/metas e relatórios reutilizam cálculos canônicos, com memória, fonte/versão e avaliações, integrados às sete skills da etapa.
  - Manifesto dos motores e primeira linha de base medida em `docs/PERFORMANCE_BASELINE.md`; não adiar a medição inicial para a avaliação de aceleradores.
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
