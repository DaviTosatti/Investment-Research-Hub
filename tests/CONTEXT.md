# Contexto de `tests/` — Testes Automatizados e Garantia de Qualidade

## 1. Missão e Objetivo (Goal)
O diretório `tests/` centraliza as baterias de testes em Python do monólito modular do Hub.
Sua missão é atuar como a **camada de auditoria e validação de invariantes** do sistema, garantindo matematicamente a precisão dos cálculos financeiros, a inviolabilidade contábil, a segurança das sessões na API, o isolamento dos titulares econômicos e a estabilidade da execução no Windows Server/Desktop e Linux.
> *Nota: Os testes de componentes e páginas web em TypeScript residem em `apps/web/tests/`.*

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Testes de Unidade (`tests/unit/`):**
  - `test_ledger.py`: Testes determinísticos dos eventos contábeis (aportes, retiradas, compras, vendas, dividendos, taxas, splits).
  - `test_ledger_adversarial.py`: Testes baseados em propriedades com `Hypothesis`, submetendo o motor contábil a sequências pseudoaleatórias extremas de eventos para provar conservação de valor e consistência de saldos.
  - `test_windows_runtime.py`: Testes de detecção de runtimes portáteis, extração e variáveis de ambiente em plataformas Windows.
- [x] **Testes de Integração com Banco de Dados (`tests/integration/`):**
  - `conftest.py`: Fixtures de ciclo de vida do PostgreSQL (testcontainers ou banco dedicado), aplicação de migrações via Alembic e clientes HTTP com `httpx.AsyncClient`.
  - `test_contracts.py`: Validação ponta a ponta dos contratos JSON da API, serialização de decimais, cabeçalhos de segurança e erros HTTP.
  - `test_portfolios.py`: Fluxo integrado de criação de titulares, carteiras, ativos, cotações e emissão de dashboard.
  - `test_native_admin.py`: Testes dos fluxos administrativos e bootstrapping de usuários.
  - `test_review_regressions.py`: Testes dedicados a prevenir regressões de segurança e concorrência (ex: saques concorrentes bloqueados quando esgotam o caixa, tentativas de reuso de chave de idempotência com corpos divergentes, revogação de sessões).
- [x] **Suíte de Verificação Nativa Windows (`tests/windows/`):**
  - `verify_native.py`: Script autônomo executado no CI Windows que valida a integridade dos binários baixados, inicialização dos serviços em caminhos com espaços e caracteres acentuados, e reinício sem corrupção de dados.

## 3. Regras de Negócio e Invariantes dos Testes
- **Evidência Real e Não Simulada:** É proibido marcar itens como "validados" na matriz de requisitos ou nos relatórios sem a execução comprovada de testes reais correspondentes.
- **Tolerância Zero a Regressões Numéricas:** Qualquer bug corrigido na contabilidade ou API deve obrigatoriamente acompanhar um teste em `test_review_regressions.py` demonstrando a falha antes da correção e o sucesso após ela.
- **Adversarial First:** Testes contábeis não devem cobrir apenas o "caminho feliz"; devem forçar cenários de:
  - Tentativa de venda de ativo que o titular não possui.
  - Tentativa de retirada de caixa maior do que o saldo disponível.
  - Dois saques concorrentes simultâneos concorrendo pelo mesmo saldo.
  - Envio de cotações com datas futuras.
  - Inserção de dados de um titular econômico por outro usuário sem autorização.

## 4. Contratos de Execução dos Testes
- Testes unitários (`tests/unit`) não requerem serviços externos, containers ou conexão de rede; executam em milissegundos.
- Testes de integração (`tests/integration`) conectam-se ao PostgreSQL real e executam o pipeline completo de migração do Alembic para garantir fidelidade ao ambiente de produção.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Cobertura completa dos casos normativos da matriz de requisitos:
    - T01 a T07 (Contabilidade, posições, saldos, custos de transação e eventos corporativos).
    - T15 (Auditoria de lançamentos contábeis).
    - T21 (Tratamento de proventos e datas de direito).
    - T25 e T26 (Métricas canônicas de retorno e conciliação).
  - Testes do importador de extratos (CSV e XLSX) com arquivos malformatados, linhas truncadas e transações duplicadas.
  - Testes do servidor de relatórios S21 (validação do conteúdo e integridade dos PDFs e planilhas geradas).
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Testes dos motores analíticos (precificação de renda fixa, valuation DCF, otimização de fronteira).
  - Testes de não-vazamento temporal em backtests (assegurar que o algoritmo em `t` não tem acesso a dados de `t+1`).
  - Testes de equivalência numérica bit-a-bit caso módulos Rust/Julia venham a ser introduzidos.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Testes de recuperação de desastres (reinício a frio a partir de um backup em ambiente limpo).
  - Testes da esteira de Comitê de IA com dados congelados (snapshots imutáveis) e simulação de divergências deliberadas.

## 6. O Que Fica Fora de Escopo
- Não colocar testes de componentes React/Next.js nesta pasta (ficam em `apps/web/tests/`).
- Não mockar o banco PostgreSQL com SQLite nos testes de integração: SQLAlchemy em SQLite mascara diferenças cruciais de dialeto, tipos e concorrência do PostgreSQL.

## 7. Verificação e Comandos
- **Executar Testes Unitários:**
  ```bash
  pytest tests/unit -v
  ```
- **Executar Testes de Integração (Requer PostgreSQL):**
  ```bash
  pytest tests/integration -v
  ```
- **Executar Suíte Completa:**
  ```bash
  pytest tests/unit tests/integration -v
  ```
