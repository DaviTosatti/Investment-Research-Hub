# Arquitetura de computação e contratos de motores

Atualizada em 05/11/2026. Fonte: Promptx.txt §§4–5,7–11. Decisão de arquitetura: **monólito modular, Python como interface científica, bibliotecas nativas adequadas e extensões adicionais somente por evidência**. Este registro não declara Rust, Julia, provedor ou IA integrados.

## Limites e fluxo

```text
Next.js/React/TS ─┐
HTTP /api/v1 ─────┼→ serviços (autorização + transações + idempotência)
MCP / wrappers ──┘           ↓ consultas              ↓ jobs persistidos
                  PostgreSQL + snapshots       worker + motores canônicos
                           ↑                          ↓
             adaptadores → originais/normalizados ← resultados + artefatos
```

Frontend apresenta, valida intenção e formata; não calcula outra versão de fórmulas. Serviços resolvem grupo/titular, snapshot, permissões, integridade e gravação. Adaptadores coletam e normalizam, preservando originais. Motores calculam sobre entradas explícitas; não fazem rede/banco silenciosamente, não recebem credenciais nem confirmam lançamentos. IA/skills interpretam resultados e usam os mesmos serviços. Exportadores consomem resultados canônicos com identidade e filtros preservados.

Frontend, API e worker podem ser processos separados no mesmo produto/repositório, sem microserviços. PostgreSQL é o banco canônico; arquivos inicialmente em armazenamento persistente versionado com interface migrável para objetos. Não acrescentar Redis/Kubernetes/serviços externos por hábito. Um mecanismo de jobs atende importação, backtest, exportação e Comitê.

### Organização observada e proposta

| Local | Situação e responsabilidade |
| --- | --- |
| `packages/engines/src/hub_finance/ledger.py` | Motor canônico de custo médio BRL com Decimal; testes de domínio e integração documentados em STATUS. |
| `apps/web` | Interface Next.js/TypeScript em integração; ver build/testes e limite de revisão visual em STATUS. |
| `hub_api` | Código em `apps/api/src/hub_api`; FastAPI/Pydantic/SQLAlchemy/Alembic e PostgreSQL integrados no recorte de carteiras. |
| `apps/worker`, `packages/providers`, `packages/mcp_server`, `packages/shared_schemas` | Propostas do prompt para capacidades futuras; adaptar à estrutura real equivalente, sem criar pastas vazias. |
| `packages/native`, `packages/julia` | Somente se houver adoção justificada. Não há implementação aprovada registrada. |

## Política de implementação

1. Medir o trabalho representativo e separar CPU, I/O, memória, preparação, solver, transporte e persistência.
2. Escolher algoritmo, estruturas/índices/lotes e reaproveitamento antes de outra linguagem.
3. Usar NumPy/SciPy/statsmodels e, quando pertinentes, SQL/Polars/pandas, CVXPY, scikit-learn ou QuantLib. Dependência instalada não valida método/convenção ou licença.
4. Avaliar Numba apenas em kernels compatíveis; não presumir compilação de objetos de domínio, pandas, Decimal ou código arbitrário.
5. Comparar Rust próprio via PyO3/Maturin se núcleo próprio ainda dominar tempo/memória/capacidade. Uma chamada trata job/lote, não cada célula. Preferir extensão no worker a novo serviço de rede.
6. Considerar Julia/JuMP quando biblioteca/formulação/algoritmo trouxer vantagem concreta; comparar build/runtime/aquecimento/solver e manutenção. JuliaCall ou processo persistente usa o mesmo mecanismo de jobs.
7. Adotar por correção, benefício útil e distribuição sustentável; registrar também quando a base já atende. Sem fator universal de aceleração e sem obrigação de usar várias linguagens.

Reaproveitar bindings de C/C++ consolidados; código próprio nessa linguagem só por necessidade específica documentada. Nunca manter motores completos Rust e Julia do mesmo módulo sem justificativa. Só um backend aprovado é selecionado por execução/versão, sem competição em cada requisição.

## Registro inicial de capacidades

| Motor / skill | Base prevista | Situação / condição de adoção |
| --- | --- | --- |
| Ledger / S01,S12 | Python Decimal/SQL NUMERIC | `average-cost-brl/1.0.1` integrado a API/banco/CSV e testado; cobertura de eventos e skills ainda parcial. Dinheiro não passa por float. |
| Ingestão/auditoria/fundamentos/macro/pares/radar / S02,S03,S07,S11,S12,S19 | Python + SQL/NumPy e tabular apropriado | Planejado; preservar IDs/tempos/escalas/nulos/rejeições/linhagem. SQL/Polars é hipótese a medir, não adoção concluída. |
| Performance/metas/renda/ETFs / S01,S09,S15 | Python e cálculo vetorial pertinente | Planejado; fluxos monetários exatos e derivados identificados; cenários estocásticos delegam S17. |
| Valuation / S04 | Python/NumPy | Planejado; DCF pequeno não requer Rust. Medir grades/sensibilidade quando houver carga real. |
| Renda fixa / S10 | Python/NumPy/SciPy; QuantLib se convenções servirem | Planejado; isolar data de avaliação/global state; validar cronograma/preço/sensibilidades. |
| Tributação / S16 | Python/SQL Decimal | Planejado; preservar titularidade/vigência/memória. Núcleo nativo só com equivalência monetária/escala/classificação/arredondamento. |
| Risco / S05 | NumPy/SciPy + preparação tabular | Planejado; medir estatísticas/caudas/matrizes; Numba/Rust só para núcleo próprio relevante. |
| Monte Carlo / S17 | Vetorização ou kernel compatível | Planejado; um contrato, RNG/streams/lotes/memória/retomada. Rust/Julia condicionais a medição. |
| Otimização / S06 | CVXPY/solver adequado ou método específico | Planejado; medir preparação, construção/canonicalização e resolução. DPP/warm start/esparsidade quando aplicáveis; outro chamador do mesmo solver não prova ganho. |
| Técnica/backtest / S14,S08 | Python + biblioteca/kernel adequado | Planejado; ordem temporal/stateful preservada. Paralelizar estratégias/janelas independentes, não eventos dependentes do mesmo caminho. |
| Eventos/anomalias / S13,S20 | Python/SQL e bibliotecas científicas pertinentes | Planejado; coletor/kernel não confirma ledger; detector novo exige versão/avaliação de falsos positivos. |
| Sentimento/Comitê/Mentor / S18,S22,S23 | Python + adaptador de IA validado e motores comuns | Planejado; rede/inferência separadas de CPU, cache com conteúdo/modelo/procedimento. IA não é necessária para contas determinísticas. |
| Relatórios / S21 | Exportadores Python e resultados persistidos | Planejado; medir consulta/montagem/gráficos/renderização; não exigir extensão própria para exportar. |

## Contrato versionado de motor

Separar **método** (pressupostos/versão), **implementação** (artefato/runtime) e **execução** (limites/configuração). Entradas/saídas tipadas declaram domínio, pré-condições, unidade/escala/moeda, calendário, ordenação, data/cutoff, ausentes e não aplicáveis. Contratos de referência como `audit_snapshot`, `analyze_fundamentals`, `value_company`, `calculate_portfolio_risk`, `optimize_portfolio`, `run_backtest`, `run_monte_carlo`, `calculate_tax` e `run_committee` são propostas a concretizar, não funções existentes afirmadas.

Arrays especificam dtype, shape/eixos, layout/contiguidade, máscaras de ausentes, ownership/lifetime e mutabilidade. Validar na fronteira; buffer incompatível é convertido explicitamente com custo registrado ou rejeitado. Preferir lotes tipados e evitar conversões repetidas pandas↔Polars↔NumPy↔nativo. Medir cópia/materialização; não prometer zero-copy universal. Snapshots compartilhados não são mutados.

Processos separados usam contrato versionado e transporte adequado ao volume, como arquivos colunares/buffers quando justificado; grandes matrizes não viram JSON automaticamente. JSON é adequado a metadados/resultados limitados. Liberação da vinculação ao interpretador segue a API do PyO3 realmente fixado e só ocorre sem uso de objetos Python, respeitando memória e sincronização.

Dinheiro/tributos atravessam linguagens como decimal exato ou inteiro escalado com limites/overflow/arredondamento definidos. Centavos não são escala universal. Matrizes científicas podem usar float64 com tolerâncias por grandeza. Mudança de dtype, ordem de redução, aproximação ou fastmath exige política numérica versionada e validação; fastmath fica desativado por padrão e nunca rege ledger/fisco.

## Jobs, paralelismo e falhas

Fila durável inicial em PostgreSQL é opção prevista, não implementação validada. Worker usa lease/lock com prazo, heartbeat, retentativas limitadas, falha examinável/dead-letter e outbox quando aplicável. Scheduler é único/dedicado; APScheduler não substitui durabilidade. Se Celery for escolhido, validar ambiente Linux/WSL2 em vez de presumir Windows nativo. Efeitos toleram entrega ao menos uma vez; não prometer exactly-once.

Job aceito tem identidade/estado persistidos antes da resposta. Estados: queued/running/succeeded/failed/cancel_requested/cancelled e recuperação documentada; resultado financeiro separa ok/partial/unavailable/failed. Recarregar/desconectar não cancela job aceito. Cancelamento é operação explícita/autorizada; cancelado não volta automaticamente à fila. Checkpoints/cancelamento cooperativo não publicam resultado parcial como completo nem deixam lançamentos parciais.

CPU intensiva roda no worker. async/await atende I/O, não acelera algoritmo. Coordenar jobs/processos/threads de BLAS/LAPACK/Polars/Numba/nativo e limites de CPU/memória/solver. Isolar RNG e datas globais de avaliação entre jobs. Sem interrupção segura da biblioteca, processo isolado permite limite rígido, preservando estado de fila; matar thread não é cancelamento seguro.

Fallback é capacidade pré-validada, explícita e identificada. Falha numérica, inviabilidade ou dado incompatível não autoriza relaxar restrição, alterar método, precisão ou solver silenciosamente. Erros previstos incluem `INSUFFICIENT_DATA`, `STALE_INPUT`, `INVALID_ASSUMPTIONS`, `INFEASIBLE_CONSTRAINTS`, `COMPUTE_BACKEND_UNAVAILABLE`, `NUMERICAL_VALIDATION_FAILED`, `RESOURCE_LIMIT`, `CONFLICT` e `FORBIDDEN`. Falha de um módulo/IA preserva funções independentes.

## Reprodutibilidade, instalação e aceitação

Manifesto completo em [MODEL_REGISTRY](MODEL_REGISTRY.md): snapshot/cutoff, método/código, implementação/artefato/build/locks, parâmetros/política, solver/RNG/streams e limites. RNG/seed iguais isoladamente não garantem trajetórias entre runtimes; usar amostras comuns ou critério estatístico. Cache inclui identidades e escolhas relevantes, inclusive execução estocástica.

Dependências fixadas, ambiente alvo declarado e CI apenas para caminhos realmente usados. Rust adotado exige Cargo.lock, build release apropriado, wheel Maturin compatível e teste de distribuição instalada no alvo limpo. Não misturar wheels Windows/Linux nem depender de CPU exclusiva do desenvolvedor. Julia adotada exige projeto/manifesto fixados, runtime/ponte compatíveis e prontidão separada de pré-compilação/aquecimento. Não exigir esses runtimes dos módulos independentes.

Aceitar migração de backend somente após equivalência de domínio/unidades/ausentes/erros e evidência T47–T56 aplicável, benefício total medido, instalação/atualização e fallback observáveis. Para solver, comparar objetivo/viabilidade/resíduos em vez de exigir pesos idênticos de ótimos múltiplos. Para backtest, comparar eventos/caixa/custos/posições, além da curva final. [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md) separa plano de medição de resultado real.

## English summary

The chosen architecture is a modular monolith with shared application services and canonical Python engine interfaces. The inspected ledger is the only engine source recorded here; no native extension or external AI/provider is certified. Scientific libraries come first; Rust and optional Julia require measured benefit, financial equivalence and sustainable distribution. Contracts cover exact money, typed buffers, immutable snapshots, persistent jobs, bounded resources and explicit failure/fallback behavior.
