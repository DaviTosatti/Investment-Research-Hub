# Linha de base de desempenho

Atualizada em 05/11/2026. Fonte: Promptx.txt §§4.5–4.6,8,10.5–10.6. **Nenhum benchmark representativo foi executado neste incremento; não há latência, consumo de memória ou aceleração medidos neste registro.** Cargas, volumes e protocolo abaixo são propostas para os motores efetivamente implementados. Metas numéricas serão definidas após uma linha de base real no ambiente alvo.

## Evidência disponível e limites

| Evidência | Situação | O que permite concluir |
| --- | --- | --- |
| Código do ledger `packages/engines/src/hub_finance/ledger.py` | Método `average-cost-brl/1.0.1` com testes registrados em STATUS. | Existe implementação inicial a perfilar; correção testada não comprova escalabilidade, latência ou ganho. |
| 59 testes de domínio/API | Comando `uv run pytest -q` passou; ver STATUS. | Relato de correção no recorte testado; não é benchmark nem validação de S01/S12 completas. |
| Integração web/API/PostgreSQL | API/PostgreSQL/CSV testados; frontend com 24 testes, tipos, lint e build aprovados. | Não há medição de desempenho fim a fim nem QA visual registrado. |
| Rust/Julia/Numba/Polars adicional | Sem implementação/adoção/benchmark confirmado aqui. | Não há ganho comparativo ou gargalo demonstrado. Não criar runtime apenas para preencher a tabela. |

## Cargas propostas

Fixtures sintéticas, identificadas e sem extratos/posições pessoais. Fixar gerador/seed, tamanho, checksum e distribuição dos dados. Volumes abaixo são exemplos iniciais ajustáveis ao propósito e à máquina; todos estão **não executados**.

| Carga | Etapa e exemplo de volume | Trabalho e verificações | Componentes a separar |
| --- | --- | --- | --- |
| B01 — ledger pequeno | 1; até 100 eventos conhecidos em duas carteiras | Depósito, compra, venda parcial/final, dividendo, taxa/imposto e split; caixa/custo/resultado conciliáveis e invariantes independentes. | Validação, ordenação/replay, escrita/leitura e agregação; isolar motor em memória de serviço persistente. |
| B02 — ingestão/reconciliação | 1; 1.000 linhas e crescimento até 100.000 operações, 5 participantes/20 carteiras | CSV e XLSX quando entregues; prévia/normalização/auditoria/confirmar, duplicatas entre arquivos e concorrentes, rejeições, retry. | Leitura/parse, mapeamento, validação, comparação/dedup, transação e armazenamento do original. |
| B03 — séries/indicadores | 1; pequeno com 20 ativos/252 observações; intermediário até 1.000 ativos/2.520 observações diárias | Identidade, consultas filtradas/paginadas, períodos/TTM, unidades/versões/ausentes; sem carregar toda a base no navegador. | Fonte simulada identificada versus fonte real, SQL/índices, materialização, preparação tabular e cálculo. |
| B04 — dashboard/CSV | 1; consultas sobre B01/B02/B03, uma e múltiplas sessões do grupo | Mesmo contexto/snapshot nos cartões/tabelas/exportação; ausência de preço e troca rápida de filtros; respostas antigas descartadas. | Banco, serviço, serialização, transporte e renderização; cache frio/quente e tamanho da resposta. |
| B05 — relatórios | 1–3 conforme formatos implementados; carteira pequena e tabela longa de 1.000 linhas | Mesmos valores/filtros/fontes; PDF/XLSX/PPTX/PNG/SVG/CSV quando presentes; acentos/negativos/ausências; arquivos abertos/renderizados. | Consulta, montagem, gráficos, escrita, renderização e persistência do artefato. |
| B06 — risco/estresse | 2; 20/100/500 ativos com 252/1.260 observações, conforme memória | Retornos/covariância/VaR/CVaR/drawdown/estresse; alinhamento/nulos/degeneração e exemplo conhecido. | Preparação/alinhamento, matrizes, estatísticas/caudas, persistência e cópias entre backends. |
| B07 — otimizações repetidas | 2; 20/100 ativos e 10/50 conjuntos de parâmetros/restrições | Mesmo estimador/objetivo/solver/tolerância, custos/caixa/limites e diagnóstico de inviabilidade; revalidar proposta após lotes. | Construção/canonicalização, setup do solver, resolução, pós-processamento; separar DPP/warm start quando compatíveis. |
| B08 — backtest por eventos | 2; 20/100 ativos, 252/1.260 dias e rebalanceamentos explícitos | Estratégia declarativa com custos/fluxos/eventos/execução; preservar sequência/caixa/posições, sem futuro; walk-forward quando presente. | Dados/universo, sinais, núcleo sequencial, contabilidade simulada, métricas e exportação. |
| B09 — Monte Carlo | 2; 1.000 e 10.000 trajetórias × 120/360 passos, até 20 ativos, ajustado ao método/memória | Mesmo snapshot/modelo/amostras/fluxos/RNG/streams e estatísticas; risco de sequência, saques e retomada. | Estimadores, amostragem, correlação, trajetória/fluxos, agregação/percentis, lote e pico de memória. |
| B10 — uso simultâneo | 1–3 conforme recursos presentes; duas sessões consultam dashboard e exportam durante um job pesado e coleta | Interface utilizável, recursos limitados e jobs recuperáveis; sem backlog indevido, duplicatas ou cancelado reexecutado. | Fila/espera, CPU/memória/thread contention, consulta/renderização, I/O externo e persistência. |
| B11 — Comitê/IA | 3; um caso com evidências fixas e especialistas pertinentes | Cálculos reutilizados, crítico verificável, fonte/modelo/limites e falha de especialista; determinismo disponível sem IA. | Preparação/evidências, motores locais, rede/inferência, ferramentas e síntese; tempo/chamadas/custo separados. |
| B12 — instalação/recuperação | 1–3; instalação alvo vazia e backup coerente do conjunto sintético | Migrar/atualizar/restaurar banco+artefatos e verificar referências; módulos habilitados e prontidão observáveis. | Instalação/build, carga de runtime, JIT/pré-compilação, aquecimento, restauração, verificação e retomada. |

Não alocar integralmente matrizes que o método pode processar em lotes só para alcançar um volume de exemplo. Estatísticas finais devem usar a população declarada; resumir visualmente trajetórias não reduz o trabalho numérico em segredo. Primeiro medir a menor carga que represente a pergunta do grupo e um crescimento justificável.

## Protocolo reproduzível

1. Registrar propósito, data, código/commit, checksum e volume da fixture, domínio coberto e resultado esperado independente. Não benchmarkar só rota HTTP vazia ou loop artificial.
2. Registrar máquina/CPU/núcleos/RAM, sistema/container/limites, armazenamento, runtime, locks, bibliotecas/BLAS/solver, backend/artefato/build/flags e instruções da CPU. Usar apenas dados não secretos do ambiente.
3. Fixar método/algoritmo, snapshot/cutoff, parâmetros, solver/restrições/tolerâncias, dtype/arredondamento e quantidade de trabalho. Para estocástico, RNG/versão/seed/particionamento/lotes. Alteração de método é experimento separado de mudança de linguagem.
4. Medir tempo total e componentes pertinentes: I/O, consulta, preparação, cálculo, canonicalização, solver, cópia/transporte, persistência e renderização. Registrar pico de memória, falhas e limites atingidos.
5. Separar instalação/build, carregamento inicial, compilação/JIT, aquecimento e execução repetida. Rust comparado em release compatível com o alvo; Julia/Numba incluem custo inicial. Não ocultar primeira execução.
6. Registrar número de observações, condições/cache de cada uma e variação; publicar mediana/faixa. Percentis só com amostra que sustente sua interpretação. Não definir repetição infinita como controle de qualidade.
7. Medir cenário isolado e concorrência B10, coordenando jobs/processos e threads de BLAS/Polars/Numba/nativo. Registrar espera na fila separada da duração do trabalho.
8. Conferir correção antes de comparar ganho: T47–T56 aplicáveis, domínio/ausentes/erros/unidades e referência independente. Para solver, objetivo/viabilidade/resíduos; para backtest, operações/caixa/custos; para simulações, amostras comuns ou teste estatístico adequado.
9. Definir metas numéricas por carga/ambiente após medir a base. Decidir por tempo, memória, capacidade ou adequação científica útil, incluindo custo de distribuição/manutenção. Se a base atende, registrar e encerrar a investigação.

## Modelo de registro de uma medição futura

Este esquema descreve o registro a preencher; **não representa uma execução realizada**.

| Campo | Conteúdo necessário |
| --- | --- |
| Identidade | benchmark_id, data, autor, commit, comando/script real e versão da carga |
| Dados | snapshot/fixture/hash, número de participantes/carteiras/operações/ativos/observações/trajetórias/passos conforme o caso |
| Ambiente | CPU/RAM/OS/limites/container, runtimes/locks, backend/artefato/build/flags, solver/BLAS |
| Configuração | método/parâmetros/política/dtype/RNG/seed/streams/lotes, jobs/processos/threads e caches |
| Medições | amostras individuais, primeira execução, componentes, mediana/faixa, memória máxima, falhas |
| Correção | testes/casos independentes, tolerâncias e divergências, sem dados financeiros pessoais nos resultados |
| Decisão | base e candidata, ganho observado no trabalho total, limites, meta derivada e adotar/manter/investigar com motivo concreto |

Resultados de testes e benchmarks podem ter artefatos sintéticos rastreáveis fora do texto; não versionar dumps de dados privados, tokens, buffers completos ou caches. Ligar registros ao manifesto do motor e à evidência de STATUS mantida pela integração.

## Critério de aceitação e regressão

Não há meta numérica homologada nem decisão de aceleração neste registro. Uma futura adoção exige correção, benefício medido no uso real e instalação sustentável no alvo; uma função isolada mais rápida não prova ganho do job. Medição de rede/inferência externa não pode ser atribuída à linguagem local.

Após atender aos critérios acordados, manter regressão enxuta dos caminhos críticos. Repetir/ampliar só por alteração, falha ou risco não resolvido. Não reduzir restrições/iterações/precisão/trajetórias para aparentar ganho, nem exigir um fator universal de speedup.

## English summary

No representative benchmark or speedup has been measured in this increment. This document defines synthetic workloads and a reproducible protocol covering end-to-end time, components, memory, cold/warm behavior, correctness and concurrent use. Numerical targets follow real baseline measurements. Native engines require practical benefit and sustainable deployment; reported unit-test success is not a performance result.
