# Contexto de `tests/` — Testes Automatizados e Garantia de Qualidade

## 1. Missão e Objetivo (Goal)
O diretório `tests/` centraliza as baterias de testes em Python do monólito modular do Hub.
Sua missão é verificar precisão financeira, integridade contábil, sessões/papéis, segregação econômica dos titulares com acesso compartilhado ao grupo e operação nos ambientes testados. Testes aprovados comprovam o recorte executado, não garantia universal nem conclusão das skills.
> *Nota: Os testes TypeScript de contratos, formatação, formulários e renderização de gráficos residem em `apps/web/tests/`; não substituem jornadas no navegador.*

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Testes de Unidade (`tests/unit/`):**
  - `test_ledger.py`: Casos determinísticos de eventos e propriedade Hypothesis (`@given`) de balanço/conservação.
  - `test_ledger_adversarial.py`: Casos determinísticos/parametrizados de frações, overflow, falhas sem mutação, avaliações após split e segregação econômica; não é o arquivo com Hypothesis.
  - `test_windows_runtime.py`: Perfil/configuração, preservação de arquivos, locks/portas, invalidação de build, migrações/cluster e falhas do supervisor, com diretórios temporários e substitutos controlados de subprocessos.
- [x] **Testes de Integração com Banco de Dados (`tests/integration/`):**
  - `conftest.py`: Cria um banco temporário exclusivo em PostgreSQL já disponível, aplica migrações Alembic, limpa tabelas entre testes e remove esse banco ao final; usa `fastapi.testclient.TestClient`, sem testcontainers ou `AsyncClient`.
  - `test_contracts.py`: Validação ponta a ponta dos contratos JSON da API, serialização de decimais, cabeçalhos de segurança e erros HTTP.
  - `test_portfolios.py`: Fluxo integrado de criação de titulares, carteiras, ativos, cotações e emissão de dashboard.
  - `test_native_admin.py`: Testes dos fluxos administrativos e bootstrapping de usuários.
  - `test_review_regressions.py`: Saques concorrentes, revogação/inativação de sessões, bloqueio de escrita por leitor, limite de login, precisão/replay, avaliação após split, guarda do CSV e limite de eventos.
- [x] **Suíte de Verificação Nativa Windows (`tests/windows/`):**
  - `verify_native.py`: Smoke executado no CI Windows após o bootstrap, verificando serviços em caminhos com espaços/acentos, primeiro acesso, operações/CSV, segunda instância, reinício com persistência e atalhos de verificação/parada.

Fontes: [ledger](unit/test_ledger.py), [adversariais](unit/test_ledger_adversarial.py), [runtime](unit/test_windows_runtime.py), [fixtures PostgreSQL](integration/conftest.py), [smoke Windows](windows/verify_native.py) e [workflow nativo](../.github/workflows/windows.yml). Downloads/hashes são responsabilidade do bootstrap PowerShell acionado pelo workflow; o smoke verifica os serviços e a persistência. A [auditoria F10](../docs/CONTEXT_PLAN_COMPARISON.md) distingue os testes existentes da aceitação integral.

## 3. Regras de Negócio e Invariantes dos Testes
- **Evidência Real e Não Simulada:** É proibido marcar itens como "validados" na matriz de requisitos ou nos relatórios sem a execução comprovada de testes reais correspondentes.
- **Regressões Numéricas:** Correções contábeis/API devem ter caso independente que reproduza a falha e comprove o comportamento corrigido, no arquivo/camada pertinente; `test_review_regressions.py` não é o único local válido.
- **Adversarial First:** Testes contábeis não devem cobrir apenas o "caminho feliz"; devem forçar cenários de:
  - Tentativa de venda de ativo que o titular não possui.
  - Tentativa de retirada de caixa maior do que o saldo disponível.
  - Dois saques concorrentes simultâneos concorrendo pelo mesmo saldo.
  - Envio de cotações com datas futuras.
  - Escrita financeira por `viewer` e acesso sem sessão válida; preservar também a consulta compartilhada autorizada de outro titular (T29/T30), sem inventar ACL usuário–titular.

## 4. Contratos de Execução dos Testes
- Testes unitários não requerem banco/serviços externos; testes do runtime usam arquivos temporários, subprocessos e sockets locais. Não há promessa universal de tempo em milissegundos.
- Integração usa PostgreSQL real configurado por `Settings`, com permissão de criar/remover o banco temporário. Alembic migra esse banco; dados são sintéticos e a limpeza deve ficar restrita às fixtures de teste.
- Entradas incluem cenários conhecidos/fixtures separados de dados pessoais; saídas são asserções e resultados reais de execução com comando/ambiente/limites, sem promover IDs normativos a casos integralmente aprovados pela contagem de testes.

## 5. Roteiro por Etapas (Ao fim das etapas)

Significados normativos e recortes por etapa: [matriz T01–T56](../docs/REQUIREMENTS_MATRIX.md), [plano](../docs/IMPLEMENTATION_PLAN.md) e Promptx §10. Os casos abaixo continuam como compromissos de cobertura, não resultados desta revisão.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Cobertura completa dos casos normativos da matriz de requisitos:
    - T01–T03: aporte sem rentabilidade artificial, compra/venda/custos e split; T04: reprocessamento sequencial/concorrente; T05: mesma operação em arquivos diferentes; T06: transferências; T07: resultados opostos não compensam apurações de amigos (segregação inicial, apuração S16 na Etapa 2).
    - T15: split/grupamento preserva patrimônio; emissão com aporte separa aporte e diluição.
    - T21: não contar o mesmo provento em série ajustada/retorno total e caixa.
    - T25: anunciado, cancelado e recebido têm efeitos distintos; T26: performance em moeda-base com câmbio e datas coerentes.
    - T08/T09: normalização de unidades/escalas e TTM sem somar acumulados como trimestres isolados; T10/T11: disponibilidade histórica e revisões sem vazamento; T12: ausência não vira zero.
  - Testes do importador de extratos (CSV e XLSX) com arquivos malformatados, linhas truncadas e transações duplicadas.
  - Testes do servidor de relatórios S21 (validação do conteúdo e integridade dos PDFs e planilhas geradas).
  - Qualidade/quarentena, cobertura/falha de fontes (T33) e T45: importar/conferir/confirmar/corrigir/reexportar conservando original, decisões e trilha.
  - T32/T44: jobs/imports sobrevivem ao reinício/reload, desconectar não cancela, cancelamento explícito não deixa lançamentos parciais nem reexecuta cancelado; T35/T36: migração e restauração inicial de banco/artefatos entregues em destino vazio.
  - Sete skills S01/S02/S12/S03/S07/S21/S23 com casos conhecidos/evals, fontes e wrappers/MCP; T27/T37/T41 na cobertura inicial, jornada A e recortes B/F, dois usuários autorizados, acessibilidade/layout T42/T43 e performance/metas coerentes.
  - Primeira linha de base medida com cargas representativas, ambiente e componentes separados; testes de correção não são benchmarks.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Testes dos motores analíticos (precificação de renda fixa, valuation DCF, otimização de fronteira).
  - Testes de não-vazamento temporal em backtests (assegurar que o algoritmo em `t` não tem acesso a dados de `t+1`).
  - Equivalência de domínio, unidades, nulos, erros e precisão/tolerâncias se Rust/Julia forem adotados (T47–T56 aplicáveis, Promptx §5.5). Dinheiro permanece exato; solver/float64/estocástico seguem política validada, sem identidade bit a bit universal.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Ampliar os testes iniciais de recuperação para desastre com o conjunto completo de dados/artefatos (restauração a frio em ambiente limpo).
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
