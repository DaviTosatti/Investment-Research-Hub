# Matriz de requisitos e evidências

Atualizada em 10/11/2026. Fonte integral: Promptx.txt, edição 04/11/2026. A matriz preserva **3 etapas, 23 skills (7/12/4), 10 skills do núcleo profissional, 23 páginas e 10 áreas**.

**Estado atual:** Etapa 1 em implementação; Etapas 2 e 3 não iniciadas. S01/S12/S21 têm a base de carteiras, auditoria e CSV em implementação, com testes do recorte descritos abaixo. S02/S03/S07/S23 e as skills das etapas posteriores permanecem não iniciadas. Nenhuma skill completa está validada. Os contratos de cobertura integral nas tabelas preservam os próximos requisitos; somente a tabela de evidências abaixo identifica funções já verificadas.

Estados permitidos: não iniciado → em implementação → pronto para revisão → validado; bloqueado por dependência externa exige causa exata e cobertura funcional remanescente. T01–T56 identificam os casos normativos do prompt, não testes já executados. Sem evidência, nenhum item passa a validado.

A [auditoria da Etapa 1](STAGE_1_AUDIT.md), código `93aafe4`, confirma as lacunas
por requisito, skill, página e rota. Os caminhos propostos nas tabelas seguintes
não são inventário de endpoints disponíveis. `/imports`, `/sources`,
`/snapshots`, `/quality` e `/lineage` ainda não existem; `/dados` mostra apenas
avaliações manuais e trilha de ações. Nenhuma skill foi concluída pela auditoria.

## Evidências do primeiro incremento da Etapa 1

| Cobertura | Estado e arquivos reais | Evidência / limites |
| --- | --- | --- |
| S01, P10/P11: titulares, carteiras e operações | Em implementação. `hub_api/main.py`, `models.py`, `hub_finance/ledger.py` | T01–T03/T15 no recorte BRL; compra/venda, custos, split, caixa, posições, titularidade. Importação, transferências, correção histórica e performance ainda pendentes. |
| S12, P22: integridade e auditoria | Em implementação. `security.py`, migrações e `portfolio_service.py` | T04/T12/T29/T30/T38 parcialmente cobertos: idempotência manual/external_id, concorrência, papéis, cotações ausentes e trilha imutável. Não comprova importação CSV/XLSX nem auditoria de demonstrações. |
| S21, P01/P21: consultas e CSV | Em implementação. `portfolio_service.py`, `/dashboard`, `/reports/positions.csv` | T41 no recorte CSV: mesmo motor/filtros, checksum e conflito se a seleção mudou; custo distinto de mercado. PDF/XLSX/PPTX e histórico persistido de análises ainda pendentes. |
| Acesso e P23 | Em implementação. `security.py`, `/members`, `/auth`, CLI | Sessão revogada/expirada, usuário inativo, leitor sem escrita, admin e proteção de origem; não implica OAuth/MCP remoto pronto. |
| Interface P01/P10/P11/P22/P23 | Em implementação em `apps/web` | Ver resultados reais de tipos/build/testes em STATUS; revisão visual e jornadas no navegador continuam separadas. |

Evidência executável: `tests/unit/test_ledger.py`, `test_ledger_adversarial.py`,
`tests/integration/test_portfolios.py`, `test_review_regressions.py` e `test_contracts.py`.
59 testes Python passaram em PostgreSQL 17.6 na validação de 05/11/2026; a interface
passou em 24 testes de contratos/formatação/gráficos, tipos, lint e build, também
verificados no GitHub Actions. Os casos
normativos T01–T56 das tabelas seguintes representam a cobertura integral futura;
esta contagem de testes automatizados não declara todos esses requisitos atendidos.

## Navegação — 10 áreas

| Área | Páginas |
| --- | --- |
| Início | P01 |
| Aprender | P02 |
| Explorar | P03, P05, P06, P07, P17 |
| Analisar | P04, P08, P09 |
| Estratégias | P15, P16 |
| Investimentos | P10, P11, P12, P13 |
| Monitoramento | P14, P20 |
| Colaboração | P18, P19 |
| Histórico | P21 |
| Administração | P22, P23 |

## Páginas — 23 contratos de cobertura

As rotas preservam a proposta do prompt; rotas equivalentes válidas podem ser mantidas. Uma página com cobertura em várias etapas não está pronta só por ter navegação ou dados sintéticos.

| ID | Página e rota proposta | Cobertura e etapa | Skills | Serviços HTTP propostos | Aceitação |
| --- | --- | --- | --- | --- | --- |
| P01 | Dashboard `/inicio` | Patrimônio, aportes, resultado, retorno, renda, evolução/benchmark, alocação, watchlist, agenda e atividades; grupo/titular/carteira. Base 1, ampliação 2–3. | S01, S02, S21, S05 | `/portfolios`, `/performance`, `/income`, `/watchlists`, `/alerts` | T01, T12, T26, T33, T40–T43 |
| P02 | Aprendizado e Mentor `/aprender` | Trilhas, glossário, exemplos executados, exercícios/histórico; explicar fórmula/dados do número em foco. 1. | S23 | `/learning` e resultados dos motores | T12, T16, T27; avaliação didática |
| P03 | Mercado e watchlists `/mercado` | Busca por identidade, séries/preços/índices/moedas, comparações e listas comuns/individuais; atraso do provedor. Base 1, técnica/eventos 2–3. | S02, S14, S13 | `/market`, `/instruments`, `/watchlists` | T10, T12, T21, T33, T40 |
| P04 | Empresas `/empresas/:instrument_id` | Balanço, DRE, caixa, margens, dívida, lucro/qualidade, comparação/evidências; consolidado/individual explícitos. 1–2. | S03, S12, S19 | `/issuers`, `/analyses/fundamentals`, `/quality` | T08–T12, T16, T56 |
| P05 | FIIs e dividendos `/explorar/fiis` | Segmentos, rendimentos/cobertura, vacância pertinente, crédito, concentração, emissões e sustentabilidade; tijolo/papel/híbridos. 2. | S09 | `/analyses/income`, `/income`, `/events` | T12, T16, T21, T25 |
| P06 | Renda fixa `/explorar/renda-fixa` | Prefixado/pós/inflação, emissor, prazo, liquidez, fluxos, curva, marcação, bruto/líquido e reinvestimento. 2. | S10, S16, S07, S05 | `/analyses/fixed-income`, `/tax`, `/macro` | T24, T26; calendários/cupons/choques |
| P07 | ETFs e globais `/explorar/globais` | Holdings/datadas, sobreposição, países/setores/moedas, benchmark, taxa, tracking difference, domicílio/distribuição. 2. | S15, S05, S16 | `/analyses/etfs`, `/market`, `/tax` | T12, T26; fundos aninhados/cobertura parcial |
| P08 | Macroeconomia `/macroeconomia` | Selic, inflação, atividade, câmbio, juros externos, calendário/expectativas; observado versus hipótese. Base 1, cenários 2. | S07 | `/macro` | T08, T10–T12, T56 |
| P09 | Valuation `/valuation` | DCF/modelos apropriados/pares, cenários, editor/sensibilidade, versões e realizado versus premissas. 2. | S04, S03, S07, S19 | `/analyses/valuation` | T13–T16, T31, T41 |
| P10 | Carteiras `/carteiras` | Titulares/contas, caixa, custo/mercado, realizado/não realizado, retorno/alocação/metas; comparação equivalente sem ranking por patrimônio. Base 1, expansão 2. | S01, S05, S06 | `/portfolios`, `/accounts`, `/positions`, `/performance` | T01–T07, T12, T26, T30 |
| P11 | Operações/importação `/operacoes` | Fatos já realizados, saldos iniciais, eventos/transferências/taxas; CSV/XLSX, mapeamento, prévia, duplicatas, confirmação/conciliação. 1. | S01, S12 | `/transactions`, `/imports` | T02–T06, T32, T38, T45 |
| P12 | Proventos `/proventos` | Anunciado, recebido e projetado separados; dividendos/JCP/rendimentos/amortizações, direito/pagamento, bruto/líquido, titular/calendário. 1–3 conforme cobertura. | S09, S13, S16 | `/income`, `/events`, `/tax` | T21, T24–T25, T41 |
| P13 | Tributação `/tributacao` | Apuração individual, categorias/custos/retenções/compensações elegíveis/vigências, pendências, demonstrativo e simulação líquida. 2. | S16 | `/tax` | T07, T24, T26, T48 |
| P14 | Riscos/cenários `/riscos` | Concentração, volatilidade, drawdown, correlação, VaR/CVaR, liquidez/câmbio/juros, estresse e Monte Carlo. 2–3. | S05, S17, S07, S20 | `/analyses/risk`, `/analyses/simulations` | T17, T22, T47, T49 |
| P15 | Otimização `/estrategias/otimizacao` | Atual/proposto, fronteira, restrições, custos, rebalanceamento e simulações salvas; sem alteração de posições reais. 2. | S06 | `/analyses/optimization` | T18–T19, T50 |
| P16 | Backtesting `/estrategias/backtesting` | Universo/datas/sinais/calendário/custos/benchmark, job, operações/curva, walk-forward e comparação. 2. | S08, S14, S05 | `/analyses/backtests`, `/jobs` | T10–T11, T20–T23, T32, T51 |
| P17 | Radar de oportunidades `/radar` | Filtros/qualidade/pares/valuation, critérios salvos, score explicável, inclusões/exclusões; encaminhar para estudo. 2. | S11 | `/screeners`, `/watchlists` | T12, T16; empates/universo/critérios versionados |
| P18 | Comitê IA `/comite` | Pergunta/contexto, especialistas pertinentes, evidências/progresso, argumentos/divergências/cenários/incertezas; decisão humana separada. 3. | S22 | `/committee`, `/jobs`, `/reports` | T27, T34; referências, crítica, injection e orçamento |
| P19 | Diário/teses `/diario` | Autor, datas, hipótese/horizonte/riscos/evidências/invalidação, revisões e expectativa original versus realizado. Base 1, assistido 3. | S01, S04, S22 como consumidores, sem nova skill | `/theses`, `/comments`, `/decisions` | T31, T35; versões/atribuição |
| P20 | Alertas/agenda `/monitoramento` | Documentos/proventos/vencimentos/eventos/gatilhos, prioridade, silêncio, adiamento, dedup, entrega e reativação. 3. | S02, S13, S20, S18 | `/alerts`, `/events`, `/schedules` | T25, T32–T33, T39 |
| P21 | Relatórios/histórico `/relatorios` | Ativo/carteira/grupo, versões/premissas/fontes/Comitê; PDF/XLSX/CSV/PNG/SVG/PPTX; seções, ordem, prévia, slides paginados e gráficos editáveis quando viável. Base 1, total 3. | S21 | `/reports`, `/artifacts` | T27, T35, T41, T46 |
| P22 | Dados/auditoria `/dados` | Fontes/uploads/cobertura/revisões/divergências/quarentena, linhagem/conciliação, impacto e reprocessamento idempotente. 1. | S12 | `/sources`, `/imports`, `/snapshots`, `/quality`, `/lineage` | T04–T05, T08–T12, T33, T56 |
| P23 | Administração/automações `/administracao` | Usuários/permissões, integrações/skills/modelos, jobs/horários/logs/consumo/saúde, backups e restauração; saúde técnica separada de atualidade/finanças. Base 1, total 3. | Transversal a S01–S23 | `/auth`, `/members`, `/admin`, `/health`, `/jobs`, `/schedules` | T28–T29, T32, T35–T37, T44, T52–T55 |

## Skills — 23 requisitos de negócio

N = núcleo profissional. Caminho previsto: `.agents/skills/<nome-tecnico>/SKILL.md`, sujeito à descoberta real do cliente. Serviços abaixo descrevem a cobertura exigida; wrappers indicados são interfaces Python propostas. S01/S12/S21 estão em implementação apenas nos recortes da tabela de evidências; as demais skills não iniciaram. Nenhuma skill possui cobertura completa validada.

| ID | Etapa / N | Nome e nome técnico | Cobertura mínima e dependências | Páginas | Serviço / wrapper proposto | Testes/avaliação |
| --- | --- | --- | --- | --- | --- | --- |
| S01 | 1 | Finanças Pessoais e Investimentos `financas-pessoais-investimentos` | Patrimônio/aportes, reserva/liquidez, metas/horizonte/inflação e cenários; orçamento opcional. Ledger, preços e performance; estocástico usa S17 na etapa 2. | P01, P10, P11, P19 | portfolio/performance/goals; `personal_finance_plan.py`, `calculate_performance.py`, `project_goals.py` | T01–T07, T21, T26 |
| S02 | 1 | Radar de Mercados `radar-mercados` | Watchlists, índices/câmbio/eventos/contexto; fonte, atraso, fechado/lacunas/conflitos/ticker; distinto de screener S11. | P01, P03, P20 | market/watchlists; `build_market_snapshot.py`, `summarize_watchlist.py` | T10, T12, T33 |
| S03 | 1 / N | Análise Fundamentalista `analise-fundamentalista` | Receita/lucro/margens/ROE/ROIC/FCF/dívida/cobertura/CAGR/F-Score aplicável; acumulados→trimestres/TTM, saldos versus fluxos, médias e reportado/ajustado. Depende S12 e documentos. | P04, P09, P17, P18 | fundamentals; `normalize_statements.py`, `calculate_fundamentals.py`, `build_ttm.py` | T08–T12, T16, T56 |
| S04 | 2 / N | Valuation Inteligente `valuation-inteligente` | FCFF/WACC, FCFE/custo próprio, dividendos/residual e pares quando adequados; cenários/sensibilidade, ponte EV-equity/ações/diluição, terminal e margem versus upside. Depende S03/S07/S19. | P09, P04, P17, P19, P18 | valuation; `run_dcf.py`, `run_dividend_model.py`, `run_residual_income.py`, `relative_valuation.py`, `valuation_sensitivity.py` | T13–T16, T31 |
| S05 | 2 / N | Gestão de Risco Quantitativo `gestao-risco-quantitativo` | Concentração, volatilidade/correlação/beta/drawdown, VaR/CVaR, estresse/incremental e liquidez/juros/câmbio conforme cobertura; janelas/sinal/caudas explícitos. | P14, P10, P15, P16, P18 | risk; `calculate_risk.py`, `run_stress_tests.py`, `risk_contribution.py` | T17, T26, T47; matriz degenerada/amostra curta |
| S06 | 2 / N | Otimização de Carteiras `otimizador-carteiras` | Markowitz/mínima variância/paridade/Black–Litterman, fronteira, views documentadas, solver/custos/turnover/limites/lotes e caixa; proposta sem execução. Depende S05/S16. | P15, P10, P18 | optimization; `optimize_allocation.py`, `risk_parity.py`, `black_litterman.py`, `build_rebalance_proposal.py` | T18–T19, T50 |
| S07 | 1 / N | Inteligência Macroeconômica `inteligencia-macroeconomica` | Juros/inflação/atividade/câmbio/emprego/liquidez, frequência/revisão, Selic meta versus efetiva, nível versus taxa, nominal/real, observado/expectativa; cenário sem causalidade inventada. | P08, P06, P09, P14, P18 | macro; `fetch_macro_series.py`, `normalize_macro.py`, `build_macro_scenarios.py` | T08, T10–T12, T56 |
| S08 | 2 / N | Backtesting de Estratégias `backtesting-estrategias` | Universo point-in-time/deslistados, sinais/execução viáveis, eventos, spread/slippage/lotes/custos, temporal treino/teste/walk-forward, tentativas/overfitting e bruto/custos/fiscal separados. Estratégias declarativas. | P16, P21, P17, P18 | backtests; `run_backtest.py`, `walk_forward.py`, `analyze_backtest.py` | T10–T11, T20–T23, T51 |
| S09 | 2 | Dividendos e FIIs `dividendos-fiis` | Yield/payout/cobertura/recorrência e sustentabilidade, classes tijolo/papel/híbrido, vacância/crédito/concentração, amortização/extraordinário separados; projeção não anualiza último pagamento como promessa. | P05, P12, P10, P14 | distributions; `analyze_distributions.py`, `analyze_fii.py`, `forecast_income.py` | T12, T16, T21, T25 |
| S10 | 2 | Renda Fixa Brasil `renda-fixa-brasil` | Prefixados/pós/inflação, públicos/CDB/LCI/LCA/debêntures conforme cobertura, curvas/fluxos/desconto/duration/convexidade, calendário/indexação/cupom/amortização; garantias/isenção verificadas. Depende S07/S16. | P06, P14 | fixed-income; `price_fixed_income.py`, `build_cashflow_schedule.py`, `calculate_duration_convexity.py`, `compare_net_yields.py` | T24, T26; feriado, defasagem, taxa negativa |
| S11 | 2 / N | Radar de Oportunidades `radar-oportunidades` | Filtros salvos/score explicável, qualidade, pesos e exclusões/universo versionados; ranking não é ordem nem probabilidade. Reusa S12/S03/S19/S04 e classes. | P17, P03, P04, P18 | screeners; `run_screener.py`, `rank_candidates.py`, `explain_screening.py` | T12, T16; outlier, empate, peso zero |
| S12 | 1 / N | Auditoria de Dados Financeiros `auditoria-dados-financeiros` | Schema, escala/unidade/períodos/chaves/duplicatas, consistência/linhagem/atualidade/disponibilidade, quarentena e impacto; correções com regra/autoria. | P22 e todas como pré-condição | quality/lineage; `audit_snapshot.py`, `reconcile_sources.py`, `validate_periods.py` | T04–T05, T08–T12, T33, T56 |
| S13 | 3 | Monitor de Eventos Corporativos `eventos-corporativos` | Coleta/interpretação de resultados/proventos/emissões/splits/fusões/controle/vencimentos; anúncio/direito/vigência/pagamento/revisão/cancelamento. Rumor não confirma ledger. Contabilidade dos eventos começa na etapa 1. | P20, P12, P10, P19, P18 | events; `ingest_corporate_events.py`, `normalize_event.py`, `assess_event_impact.py` | T03, T15, T25, T39 |
| S14 | 2 | Análise Técnica `analise-tecnica` | Médias/RSI/MACD/ATR/bandas/volume/regras, OHLCV, aquecimento/suavização, eventos e instante de sinal, sem dado futuro. | P03, P16, P17 | technicals; `calculate_technical_indicators.py`, `evaluate_signal_rules.py` | T10, T20–T21; gaps/janela incompleta |
| S15 | 2 | ETFs e Investimentos Globais `etfs-investimentos-globais` | Composição/benchmark/taxa/tracking difference/país/setor/moeda/domicílio, acumulação/distribuição e overlap direto/indireto; listagem não equivale a exposição cambial. Depende holdings/câmbio/S16. | P07, P10, P14, P15, P18 | etfs/exposure; `analyze_etf.py`, `calculate_holdings_overlap.py`, `decompose_currency_returns.py` | T12, T26; fundos aninhados e taxa já embutida |
| S16 | 2 / N | Tributação e Renda Líquida `tributacao-renda-liquida` | Por titular/residência/competência, comum/day trade/FII/FIAGRO/renda fixa/fundos/proventos/exterior conforme validação, custos/retenções/compensações elegíveis/vigência e pendências; estimado versus completo. | P13, P12, P06, P07, P10, P16 | tax; `classify_tax_events.py`, `calculate_tax.py`, `compare_net_returns.py` | T07, T24, T26, T48 |
| S17 | 2 | Simulador Monte Carlo `simulador-monte-carlo` | Único motor: metas/fluxos/inflação/retiradas/correlação/risco de sequência, paramétrico/bootstrap temporal, RNG/seed/streams/lotes, percentis e erro amostral; não reduzir trabalho silenciosamente. | P14, P10, P18 | simulations; `simulate_portfolio.py`, `simulate_goal_probability.py` | T22, T49; esgotamento/convergência |
| S18 | 3 | Analisador de Sentimento `analise-sentimento` | Conteúdo legítimo, temas/tom/posição, evidências curtas, dedup/entidades/data, ambiguidades/inconclusivo; tom não é efeito econômico. | P03, P20, P19, P18 | sentiment; `deduplicate_news.py`, `classify_sentiment.py`, `extract_evidence.py` | T10, T34; ironia, homônimos e injection |
| S19 | 2 | Comparador de Setores `comparador-setores` | Pares por atividade/modelo/geografia/porte, métricas/dispersão/mediana e limites econômicos; amostra/período/moeda/ausentes/exclusões. Depende S03/S12. | P04, P09, P17, P18 | peers; `select_peers.py`, `compare_sector_metrics.py` | T08, T12, T16; negativos/outliers/amostra pequena |
| S20 | 3 | Detecção de Anomalias `deteccao-anomalias` | Estatística robusta/sazonalidade/regimes, preço/volume/fundamentos/séries; distinguir dado ruim/evento/economia, treino temporal e falsos positivos; não diagnosticar fraude por desvio. | P20, P22, P14, P18 | anomalies; `detect_anomalies.py`, `detect_regime_changes.py` | T03, T12, T33; drift/conjunto rotulado |
| S21 | 1, amplia até 3 | Relatórios e Dashboards `relatorios-dashboards` | Templates próprios, resultados canônicos, PDF/XLSX/CSV/PNG/SVG/PPTX, versões/fontes/filtros/idioma/seções/prévia, gráficos editáveis quando viável e slides paginados. Motor/templates funcionais na etapa 1. | P21, P01 e exportações | reports/artifacts; `export_report.py`, `export_workbook.py`, `build_presentation.py` | T27, T41, T46 |
| S22 | 3 / N | Comitê de Investimentos IA `comite-investimentos-ia` | Snapshot/auditoria/especialistas relevantes, análises independentes, crítico, verificação determinística, divergências/síntese/evidências/versões e decisão humana; sem votação como confiança. | P18, P19, P04, P10, P17, P21 | committee; `run_committee.py`, `build_evidence_bundle.py`, `validate_committee_claims.py`, `synthesize_committee.py` | T27, T34; fonte inexistente, timeout, custo, injection |
| S23 | 1 | Mentor de Investimentos `mentor-investimentos` | Glossário/trilhas/exercícios, linguagem por nível, contexto/número/fórmula da tela e exemplo reproduzível, ausências e próximo estudo. Reusa motores; não cria cálculo em prompt. | P02 e explicações contextuais | learning; `run_teaching_example.py` | T12, T16, T27; fidelidade ao número e exemplo versus posição |

As duas skills originais S01/S02 foram mencionadas em um ZIP. Nenhum ZIP correspondente foi localizado no material fornecido; não alegar importação/revisão de seu conteúdo. Todas as skills exigem gatilhos/fronteiras, entradas/defaults/validações, fontes/motores, procedimento/interrupção, saída/evidências, casos normais/adversos e critério de conclusão. Wrappers instaláveis oferecem `--help`, JSON/artefato e erros consistentes; não dependem do cwd nem duplicam fórmulas. Agentes de desenvolvimento ficam separados do catálogo.

## Requisitos transversais

As linhas abaixo preservam requisitos integrais; algumas possuem cobertura parcial no primeiro incremento, sem conclusão integral presumida. Consulte as evidências acima e a auditoria para o que existe. Referências § remetem ao Promptx.txt; caminhos de serviço/pacote são propostas. Títulos/códigos de testes não significam execução.

| ID / fonte | Requisito verificável | Páginas / skills | Serviço ou destino proposto | Aceitação |
| --- | --- | --- | --- | --- |
| R01 / §0,1,12 | Exatamente 3 etapas, 23 skills 7/12/4, 10 núcleo, 23 páginas/10 áreas; sem SaaS, promessa de retorno ou ordens. | Todas | Catálogo e plano; serviços de domínio | Contagem e revisão funcional; simulação isolada |
| R02 / §0,5,6 | Usuário/autoria separados de titular econômico; conta/carteira/documento/tributo preservam titular. Consolidado analítico. | P10–P13, P19, P23 / S01,S12,S16 | auth/members/owners/portfolios/accounts | T06–T07, T29–T30 |
| R03 / §0,9 | Login/sessões individuais, vínculo ao grupo, admin/member/viewer e autorização nos serviços. Dados comuns não expõem credenciais; escopo de grupo em toda busca por ID. | Todas | auth + políticas compartilhadas API/MCP | T28–T30 |
| R04 / §2 | Identidade fintech escura própria/tokens/componentes; excluir padronizar-dashboards/Adquirência/Outlook automático. | Todas / S21 | `apps/web`, templates Hub | Capturas reais e revisão; T42–T43 |
| R05 / §2 | pt-BR e cópia inglesa; moedas/unidades/datas claras; teclado/foco/leitor/contraste/movimento/toque; 1440/1024/768/390 px. | Todas / S21,S23 | UI/i18n/design system | T42–T43, T46 |
| R06 / §2 | Carregando/vazio/erro/parcial/antigo/normal; última informação válida identificada; falha de fonte não apaga carteira. | Todas / S02,S12 | consultas/quality/freshness | T12, T33–T34 |
| R07 / §2 | Contexto, período, moeda e versão iguais em cards/gráficos/tabelas/arquivos; resposta antiga descartada; preferências/rascunhos; timeline independente do documento. | Todas / S01,S21 | contratos de consulta/UI/cache | T40–T41, T44 |
| R08 / §4 | Monólito modular Next/TS + FastAPI/Pydantic/SQLAlchemy/Alembic/Postgres; domínios/motores/adaptadores separados, locks e migrações. | Todas | `apps/web`, `apps/api`, `packages/*` | T35 e instalação; lint/tipos/build |
| R09 / §5.1 | IDs internos estáveis, emissor/instrumento/listagem separados, símbolo com vigência/bolsa/classe/moeda; capitalização sem duplicação de ações entre classes. | P03–P17,P22 / S02,S03,S12,S15 | instruments/issuers | T15–T16; troca ticker/dupla listagem |
| R10 / §5.2 | Envelope econômico/divulgação/disponibilidade/coleta, fonte/hash/versão/moeda/unidade/escala/escopo e snapshot; originais/normalizados/derivados distintos, revisões preservadas. | Todas / S12 | sources/documents/snapshots/lineage | T08–T11, T35, T56 |
| R11 / §5.3 | Interfaces preços/fundamentos/macro/eventos/notícias/curvas/calendários/holdings, fontes oficiais e alternativas de comprovação; verificar docs/licença/limites/paginação/prioridade e reconciliação. Sem scraping exclusivo ou mock como integração. | P03–P09,P20,P22 / S02,S03,S07,S12–S15,S18 | `packages/providers`, catálogo | T10–T12, T33; contrato por fonte |
| R12 / §5.4 | Qualidade válido/incompleto/desatualizado/divergente/quarentena/indisponível; null com motivo, tolerância por grandeza e atualidade específica. | Todas / S12 | quality + contratos de resultado | T08–T12, T33, T56 |
| R13 / §5.5 | Run identifica dados/as-of/cutoff, método/código, motor/artefato/build/locks, parâmetros/política/solver/RNG/recursos, qualidade/saídas; campos não aplicáveis explícitos. IA conserva prompt/modelo/evidências/saída. | Todas / S01–S23 | analysis/run manifest | T22, T27, T41, T47–T55 |
| R14 / §5.5 | Cache de coleta separado de cálculo; inclui snapshot/método/implementação/política/solver/parâmetros e RNG/streams/execução estocástica; não apenas ticker. | Todas | cache/snapshots/analyses | T22, T41, T49, T52 |
| R15 / §6.1 | Ledger imutável e balanceado; posições/caixa derivados; campos de titular, carteira, conta, instrumento, valores, moeda, negociação/liquidação, fonte/externo/chave, autoria/revisão/estorno. | P10–P13,P22 / S01,S12,S16 | ledger/transactions/positions | T01–T07, T15, T38, T48 |
| R16 / §6.1 | Eventos incluem aporte/retirada/compra/venda/transferência/câmbio/corretagem/taxa/imposto/dividendo/JCP/rendimento/cupom/amortização/split/grupamento/bonificação/subscrição/conversão/incorporação/encerramento. Exigir parâmetros/documentos para complexos. | P10–P13,P20 / S01,S12,S13,S16 | domínio de eventos; cobertura por etapa | T02–T06, T15, T21, T25; suportado versus indisponível |
| R17 / §6.1,4.6 | Decimal/NUMERIC em dinheiro/fisco, escala por grandeza, arredondamento explícito e conversões científicas derivadas; sem fastmath no ledger/fisco ou float como armazenamento canônico. | P10–P16 / S01,S05,S06,S08,S10,S16,S17 | política numérica/motores | T02, T24, T48, T53, T56 |
| R18 / §6.2,9.1 | CSV/XLSX com encoding/colunas/números/datas/moeda, prévia/totalizadores/erros/duplicatas/efeitos e confirmação; original/mapeamento/importador/decisão preservados, cópia local da origem. | P11,P22 / S01,S12 | imports + ledger | T04–T05, T32, T45 |
| R19 / §6.2,9.1 | Idempotência transacional em retries/concurrência/arquivos distintos, chave econômica e origem; chave igual com corpo diferente é conflito; ambiguidade exige conciliação. | P11,P22,P23 / S01,S12 | transactions/imports/outbox | T04–T05, T32, T38 |
| R20 / §6.3 | Aporte/fluxo/caixa/renda/custo/realizado/não realizado distintos; TWR, MWR/XIRR, Dietz explicitamente aproximado, IRR sem/múltiplas raízes; benchmark equivalente em período/moeda/calendário/retorno. | P01,P10,P21 / S01,S05,S21 | performance | T01–T02, T06, T21, T26 |
| R21 / §6.3–6.4 | Consolidar mesma data e fluxos, sem média simples; neutralizar só transferências internas ao universo; entre titulares tem natureza própria. Câmbio datado/origem/apresentação; preço ajustado e provento sem dupla contagem. | P01,P10–P14 / S01,S05,S09,S15,S16 | consolidation/performance/fx | T06–T07, T21, T26 |
| R22 / §6.4 | Custo separado de mercado; sem cotação não fabricar valor. Última avaliação com data/método; renda fixa distingue curva, mercado, saída e vencimento. | P01,P06,P10 / S01,S10 | pricing/positions | T12, T33; ausência manual/antiga |
| R23 / §8 S03,S07,S19 | Acumulado/trimestre/TTM/saldos/médias e métricas setoriais válidos; pares comparáveis, frequências macro/revisões e conhecido na data. | P04,P08,P09,P17 / S03,S07,S12,S19 | fundamentals/macro/peers | T08–T12, T16, T56 |
| R24 / §8 S04 | DCF coerente FCFF/FCFE/taxa/moeda/inflação, imposto operacional sem benefício fiscal duplicado, terminal r>g, ponte/dívida/caixa/NCI/diluição; upside versus margem e cenários sem probabilidades inventadas. | P09 / S04 | valuation + registry | T13–T16 |
| R25 / §8 S05,S06 | Risco com sinal/unidades/janela/horizonte/caudas/degeneração; sem regra universal raiz-tempo. Otimização explicita estimadores/regularização/views/solver, inviabilidade e revalida lotes/custos/caixa/limites. | P14–P15 / S05,S06 | risk/optimization | T17–T19, T47, T50 |
| R26 / §8 S08,S14 | Backtest com conhecimento histórico/ativos deslistados, eventos/sinais/execução, ajustes/custos/liquidez/treino temporal/walk-forward, tentativas/sensibilidade; sem código arbitrário; bruto/custos/fiscal separados. | P03,P16 / S08,S14 | backtests/technicals | T10–T11, T20–T23, T51 |
| R27 / §8 S09,S10,S15 | Métricas próprias por classe: renda recorrente/extraordinária/amortização; calendário/indexação/cupons/garantia/isenção verificadas; holdings datadas/overlap/moeda/domínio/taxa sem dupla cobrança. | P05–P07,P12 / S09,S10,S15 | motores de classe | T16, T21, T24–T26 |
| R28 / §8 S16 | Regras oficiais por jurisdição/residência/categoria/competência/vigência/versão/fonte/arredondamento/revisão; ano do fato versus exercício; sem compensação entre amigos, perda futura retroativa ou transmissão/pagamento automáticos. | P13,P06,P12 / S16 | tax/rule registry | T07, T24, T26, T48 |
| R29 / §8 S17,5.5 | Um Monte Carlo; modelo/amostras/RNG/seed/streams/retomada/lotes/recursos, bootstrap temporal, percentis/erro/retiradas; seed não garante igualdade entre runtimes, não reduzir população silenciosamente. | P14,P10 / S17,S01,S05 | simulations | T22, T49 |
| R30 / §8 S21,2 | Templates próprios e relatórios canônicos: PDF/XLSX/CSV/PNG/SVG/PPTX, seções/ordem/prévia/idioma/filtros/fontes, gráficos editáveis quando viável, slides longos paginados; abrir sem Office e priorizar Excel 2024, sem COM. | P21 e exportações / S21 | reports/artifacts | T27, T41, T46 |
| R31 / §4.2,9.1 | Um mecanismo de jobs durável; lease/heartbeat/retries limitados/falha examinável/outbox; scheduler único; efeitos toleram ao menos uma entrega, sem promessa exactly-once. | P11,P16,P18,P21,P23 / Transversal | jobs/worker/scheduler | T04, T32, T39, T54 |
| R32 / §4.2,9.1–9.2 | job_id persistido, progresso/timeout/retomada e cancelamento explícito/autorizado; desconectar página não cancela; cancel_requested/cancelled distintos de falha; cancelado não reentra; efeitos financeiros atômicos. | P11,P14–P16,P18,P21,P23 | jobs + contratos API/MCP | T32, T44, T54 |
| R33 / §4.5–4.6,10.5–10.6 | Medir antes de Rust/Julia; um backend aprovado por execução; referência independente/fallback validado, tipagem de buffers/ownership/ausentes, sem rede/segredos/mutação em kernels; locks/wheels/CPU/distribuição e política numérica. | Todas as análises / Transversal | engines + compute/performance docs | T47–T56 |
| R34 / §9.1–9.2 | HTTP /api/v1/OpenAPI/requests-responses tipados, paginação/filtros/ordem estáveis, limites/upload, version/ETag e GET sem escrita; MCP Streamable HTTP SDK fixado, OAuth/OIDC validado e serviços comuns; artefatos autorizados acessíveis. | Todas / Transversal | API/MCP/contracts | T27–T31, T37–T38, T41 |
| R35 / §9.2–9.4 | Cliente OAuth não é pessoa; sujeito+emissor, audiência/recurso/escopos, associação e políticas de serviço; consulta compartilhada. Sem SQL/Python/shell arbitrário, endpoint privado exposto ou localhost presumido acessível ao ChatGPT. | P23 e ferramentas / Transversal | auth/MCP/network docs | T28–T30, T37 |
| R36 / §9.4,8 S22 | IA por tarefa, modelo/API real verificados, chaves no servidor, tempo/chamadas/custo/concorrência limitados; documento é dado, não instrução; indisponibilidade da IA não bloqueia determinismo. | P02,P18,P20 / S18,S22,S23 | model adapter/evidence/policies | T34; injection/custo/schema de chamada |
| R37 / §8 S22 | Comitê segue 10 passos: fixar/auditar/escolher/calcular/independência/crítica/verificar/resolver/sintetizar/salvar; fatos/modelos/premissas/prós/contras/divergências/cenários/lacunas/invalidação/julgamento humano separados; sem consenso/confiança por voto. | P18,P19,P21 / S22 | committee/evals | Referência real, números, crítica verificável, timeout/inconclusivo |
| R38 / §8.3.1 | Teses preservam original, autoria/datas/horizonte/motivos/riscos/fontes/anexos/versões; comentários/menções internos, conflito concorrente rastreável; desempenho do preço não mede sozinho raciocínio. | P19,P18,P21 / S22 e consumidores | theses/comments/decisions | T31, T35 |
| R39 / §8.3.2 | Alertas de eventos/limites/premissas/macro/metas/saúde/relatórios com escopo/fonte/tolerância/frequência/destinatários/silêncio/dedup/reativação e prévia/teste; não disparar por preço antigo. Internos primeiro; externos só configurados expressamente. | P20,P23 / S02,S13,S18,S20 | alerts/schedules | T25, T33, T39 |
| R40 / §8.3.2,11.1 | America/Sao_Paulo na apresentação/agendamento, timezone canônico e calendário da bolsa; máquina local precisa estar ligada; lacunas/catch-up/última coleta sem avalanche de alertas atrasados. | P03,P08,P20,P23 | calendars/scheduler/ingestion | T20, T32–T33, T39 |
| R41 / §11 | Caminho principal de instalação real Linux/WSL2 ou nativo validado; local/híbrido/24h sem três produtos. Scripts bootstrap/admin/migrate/start/stop/health/test/update/backup/restore, demo isolada, supervisão e volumes persistentes. Docker/Redis/K8s só quando necessários. | P23 / Transversal | scripts/infra/runbooks | T32, T35–T36, T44, T55 |
| R42 / §11.2,9.3 | SSH/Tailscale opcionais com chaves/contas individuais, preservando rede; não alegar conexão pessoal testada sem teste. Site, SSH e MCP são acessos distintos; segunda conta/cliente MCP realmente testados quando disponíveis. | P23 / Transversal | acesso/runbooks | T28–T30, T37; evidência de conexão |
| R43 / §11.4 | Logs request/job/user/provider/motor/artefato/duração/componentes/recursos sem segredo/extrato/buffer; liveness/readiness/fonte/freshness/motor separados; warmup e fallback identificados. SKIP LOCKED só para fila apropriada, não carteira parcial. | P22,P23 / Transversal | observability/health/jobs | T32–T34, T52, T54 |
| R44 / §11.5 | Backup coerente banco+originais+snapshots+artefatos+config, hashes/schema/retenção/destino/periodicidade, credenciais separadas; restaurar em vazio e verificar relações. | P23 / Transversal | backup/restore | T35–T36 |
| R45 / §1,4.4,7,12 | Skills curtas/acionáveis com referências/wrappers/evals; descobrir diretório real; preservar agentes de manutenção separados; ausência do ZIP explícita; não afirmar modelos/esforço ou funcionalidades sem evidência. | P23 / S01–S23 | catálogo/agents/docs | Revisão de contratos e avaliação por skill |
| R46 / §1,10,12 | Testes relevantes conhecidos/independentes, jornadas A–F, conjuntos separados de eval, matriz/STATUS/HANDOFF datados e incremento verificado com Conventional Commits/push pelo integrador; sem dados pessoais/segredos no Git. | Todas | tests/docs/CI/review | Evidência de comandos/resultados/commit; sem conclusão só documental |
| R47 / §10.5 | Baselines reais com volumes/ambiente/cache/threads, componentes/memória/falhas, frio/JIT/aquecido, variação e concorrência; metas depois de medir, sem latência/aceleração universal ou linguagem confundida com método. | Todas / motores usados | benchmarks + PERFORMANCE_BASELINE | Medições reproduzíveis, T47–T56 quando aplicáveis |

## Catálogo normativo de testes — T01–T56

**O catálogo abaixo define aceitação integral.** Os testes do primeiro incremento cobrem os recortes identificados na tabela de evidências, sem homologar automaticamente cada caso normativo inteiro. Cada registro deve conter caminho real, comando, resultado, data, ambiente e commit verificado. Casos nativos só se aplicam aos caminhos efetivamente adotados; não criar dependência Rust/Julia para cumprir teste condicional.

| ID | Comportamento obrigatório | Requisitos principais |
| --- | --- | --- |
| T01 | Aporte de R$ 10.000 sem variação de preço aumenta patrimônio, sem lucro ou rentabilidade artificial. | R15,R20 |
| T02 | Compra, venda parcial, taxa e custo conciliam caixa, posição e resultado. | R15,R17,R20 |
| T03 | Split 1:2 ajusta quantidade/custo/preço unitário sem ganho instantâneo. | R15,R16 |
| T04 | Reprocessamento sequencial e concorrente não duplica o mesmo fato. | R18,R19,R31 |
| T05 | Arquivos distintos com a mesma operação são conciliados. | R18,R19 |
| T06 | Transferência do mesmo titular preserva custo/retorno; entre titulares é classificada. | R02,R16,R21 |
| T07 | Resultados opostos de amigos mantêm apurações fiscais separadas. | R02,R28 |
| T08 | Unidades/milhares/milhões equivalem após normalização. | R10,R12,R23 |
| T09 | TTM não soma quatro valores acumulados como trimestres isolados. | R23 |
| T10 | Informação divulgada em maio não participa de decisão em abril. | R10,R23,R26 |
| T11 | Revisão posterior não vaza para análise/backtest anterior. | R10,R26 |
| T12 | Ausência continua ausente, nunca zero fabricado. | R06,R12,R22 |
| T13 | FCFF/FCFE usam taxa correspondente; sem WACC indevido. | R24 |
| T14 | g terminal >= taxa de desconto é rejeitado com explicação. | R24 |
| T15 | Split/grupamento preservam patrimônio; emissão com aporte separa aporte e diluição. | R09,R16,R24 |
| T16 | Bancos e FIIs não recebem métricas incompatíveis por default. | R23,R27 |
| T17 | VaR/CVaR/drawdown seguem a convenção em exemplo conhecido. | R25 |
| T18 | Otimização inviável não viola limites escondidos. | R25 |
| T19 | Arredondar lotes não cria caixa negativo nem excesso de concentração. | R25 |
| T20 | Sinal no fechamento respeita o primeiro instante de execução viável. | R26,R40 |
| T21 | Série ajustada/retorno total e caixa não contam o mesmo provento duas vezes. | R20,R21,R26,R27 |
| T22 | Snapshot/implementação/config/RNG/seed/streams reproduzem simulação no escopo declarado; mudanças alteram identidade. | R13,R14,R29 |
| T23 | Custos/spread/slippage entram no instante correto do backtest. | R26 |
| T24 | Mudança fiscal preserva apuração da vigência anterior. | R28 |
| T25 | Provento anunciado/cancelado/recebido tem efeitos distintos. | R16,R27,R39 |
| T26 | Performance em moeda-base usa câmbio e datas coerentes. | R20,R21,R28 |
| T27 | Script, REST e MCP retornam métricas equivalentes para a mesma entrada. | R13,R30,R34 |
| T28 | Credencial expirada, audiência errada ou escopo insuficiente impede ação. | R03,R34,R35 |
| T29 | Pessoa sem vínculo ao grupo não obtém dados adivinhando IDs. | R02,R03,R35 |
| T30 | Membro autorizado consulta dados compartilhados de outros titulares. | R02,R03,R35 |
| T31 | Edição concorrente gera conflito rastreável e conserva texto anterior. | R34,R38 |
| T32 | Reinício preserva/retoma importação/job; desconectar não cancela; cancelamento explícito não deixa efeitos parciais. | R19,R31,R32,R41 |
| T33 | Fonte falha conserva dado identificado/idade sem inventar preço. | R06,R11,R22,R39,R43 |
| T34 | Falha de IA preserva recursos independentes. | R06,R36 |
| T35 | Migração preserva operações, snapshots, teses e relatórios. | R08,R10,R38,R41,R44 |
| T36 | Restaurar em destino vazio recupera banco e artefatos coerentes. | R41,R44 |
| T37 | Cliente MCP real autentica/descobre/chama análise e recupera job/artefatos acessíveis; versões registradas. | R34,R35,R42 |
| T38 | Mesma chave idempotente com payload diferente é rejeitada. | R19 |
| T39 | Retry de alerta não duplica notificações indevidamente. | R31,R39,R40 |
| T40 | Troca de titular/carteira/período/moeda sincroniza visão e invalida resposta antiga. | R07 |
| T41 | Exportação conserva snapshot, filtros e parâmetros do resultado. | R07,R13,R30 |
| T42 | Layout nas quatro larguras não sobrepõe/corta gráficos nem oculta ações. | R04,R05 |
| T43 | Teclado/foco/contraste/erros são utilizáveis. | R04,R05 |
| T44 | Reload recupera jobs e preferências válidas. | R07,R32,R41 |
| T45 | Importar/conferir/confirmar/corrigir/reexportar preserva origem e trilha. | R18,R19 |
| T46 | PDF/PPTX/XLSX abrem e passam revisão visual com tabelas longas, negativos, acentos e ausências. | R05,R30 |
| T47 | Acelerado versus referência preserva domínio/unidades/nulos/erros e tolerâncias; canais identificam o motor aprovado. | R13,R33 |
| T48 | Dinheiro atravessa banco/serviço/nativo com precisão/escala/arredondamento e overflow validados. | R17,R28,R33 |
| T49 | Trajetórias comparadas usam amostras comuns ou critério estatístico apropriado; retomada preserva streams. | R14,R29,R33 |
| T50 | Solver conserva viabilidade/objetivo/resíduos/limites; ótimos múltiplos não exigem pesos idênticos. | R25,R33 |
| T51 | Backtest acelerado preserva sequência/operações/caixa/posições/custos/disponibilidade, além da curva. | R26,R33 |
| T52 | Extensão indisponível/incompatível falha ou usa fallback validado/identificado; histórico/cache não confundem identidades. | R14,R33,R43 |
| T53 | Buffers/máscaras/layout/ownership/lifetime respeitam contrato e não mutam snapshots; incompatibilidade é explícita. | R17,R33 |
| T54 | Nativo cancelado/timeout/retry/concorrência preserva limites/estados/atomicidade e não reexecuta cancelado. | R31,R32,R33,R43 |
| T55 | Pacote compilado instala e roda caso conhecido no alvo limpo, sem dependência acidental do compilador/CPU local. | R33,R41 |
| T56 | Caminho tabular adotado conserva datas/escalas/ausências/IDs/ordem/rejeições; aproximações têm tolerância validada. | R10,R12,R17,R23,R33 |

## Jornadas e conclusão

| Jornada | Encadeamento | Páginas / skills principais |
| --- | --- | --- |
| A | Pesquisar empresa → auditar → fundamentos → aprender → tese → relatório. | P03/P22/P04/P02/P19/P21; S02/S12/S03/S23/S21 |
| B | Carteira → importar → conciliar → posições/retorno → provento → líquido individual. | P10/P11/P22/P12/P13; S01/S12/S09/S16 |
| C | Valuation → cenários → efeito na carteira → proposta → Comitê. | P09/P14/P15/P18; S04/S05/S06/S22 |
| D | Estratégia → backtest → custos/vieses → períodos → exportação reproduzível. | P16/P21; S08/S14/S05/S21 |
| E | Evento → mudança → alerta interno → revisão de tese com original preservado. | P20/P19/P18; S13/S18/S20/S22 |
| F | Reiniciar/atualizar → retomar → verificar → restaurar em instalação limpa. | P23/P22/P21; serviços comuns |

Para validar uma skill: contrato funcional + cálculo canônico + dados suportados/fixtures separadas + serviço e MCP quando aplicável + tela ligada com falhas + SKILL.md/referências/wrapper executáveis + avaliações realmente executadas + origem/versão/limites + exportação/histórico + operação documentada; motores intensivos também exigem decisão/precisão/linha de base e, se nativos, benefício/distribuição comprovados. Um CSV básico, uma página estática ou um diretório de skill não conclui uma skill inteira.

## English summary

This initial matrix maps all 23 pages and 23 skills to three stages, ten navigation areas, proposed services, 47 crosscutting requirements, 56 normative tests and six end-to-end journeys. The evidence overlay records the verified first-slice accounting, API and CSV behavior; full skills remain incomplete. Remaining proposed paths and normative test identifiers are not implementation claims. Stage completion and individual skill completion require integration review and recorded evidence.
