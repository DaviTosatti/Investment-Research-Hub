# Progresso verificável

Atualização: 05/11/2026 — America/Sao_Paulo.

## Estado do produto

| Etapa | Estado | Evidência atual |
| --- | --- | --- |
| 1 — Fundação, experiência visual, dados e acompanhamento | Em implementação | Primeiro fluxo de carteiras integrado; motor e API verificados; requisitos restantes preservados |
| 2 — Análise avançada, classes de ativos e estratégias | Não iniciada | Escopo preservado no plano e na matriz |
| 3 — Comitê IA, colaboração, monitoramento e operação completa | Não iniciada | Escopo preservado no plano e na matriz |

Nenhuma etapa ou skill completa foi validada neste ponto.

## Registro de entregas

| Incremento | Mudança | Validação | Publicação |
| --- | --- | --- | --- |
| E1.01 | Inventário, referência integral, plano, matriz e padrão de commits | SHA-256 do original preservado; 23 skills, 23 páginas e exatamente 3 etapas conferidas | [`a198336`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/a1983363773ce1a10be280e6cbad9744fa208705), push confirmado |
| E1.02 | Motor de eventos Decimal, lançamentos balanceados e ambiente Python/PostgreSQL | 10 testes de domínio, incluindo propriedades com Hypothesis; mypy sem erros; PostgreSQL 17.6 iniciado | [`b882a3f`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/b882a3f4fe7cd71ca9770e23f4ba98e34578399b), push confirmado |
| E1.03 | API autenticada, papéis, titulares separados, contas/carteiras, ativos/listagens, eventos imutáveis, avaliações, painel e CSV | 50 testes passaram (42 domínio/revisão e 8 integração PostgreSQL); concorrência, falta de caixa, isolamento por titular, sessão, origem e persistência; Alembic sem divergência | [`2ee03d9`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/2ee03d90f4e64a38eb52be9b1f95b46ea5e68bc0), push confirmado |
| E1.04 | Contratos monetários exatos e proteção do limite de histórico | 59 testes passaram; inclui saques concorrentes, revogação, bloqueio de tentativas, bruto de grande precisão, cotação/split no mesmo dia, CSV após mudança e limite de eventos | [`2cb0ddb`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/2cb0ddbf675947b4b908eac2d6eb1403e1ee55bb), push confirmado |
| E1.05 | Referências visuais aprovadas | Onze imagens examinadas no chat; critérios e aplicação por etapa em VISUAL_REFERENCES | [`ea2e8bc`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/ea2e8bc0deafa929b0088f3d935f3f9585555f1f), push confirmado |
| E1.06 | Interface Next.js integrada: login, filtros, carteiras, operações, avaliações, administração, auditoria e CSV; composição baseada nas referências | 24 testes web passaram: precisão, fuso, formulários, idempotência, paginação, cancelamento, snapshot CSV e gráficos; typecheck, lint e build passaram | [`e421e48`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/e421e48c64073261e73da2beece40e5a1383b05b), push confirmado |
| E1.07 | CI para API/PostgreSQL e frontend, scripts de bootstrap/check e template de PR | Scripts com sintaxe Bash validada; comandos correspondentes aprovados localmente; execução remota será consultada após push | Commit de CI que introduz este registro |

## Em implementação

Verificações automatizadas no GitHub e documentação de instalação/continuidade.
Contrato de integração: [API_CONTRACT.md](API_CONTRACT.md).

## Verificação visual

O painel segue a composição FinSight/Stockly, com navegação inspirada em Chainx:
indicadores compactos, histórico amplo, alocação em rosca e tabela de posições.
Os valores vêm da API; histórico e alocação usam custo explicitamente identificado.
Os testes de renderização cobrem dados e semântica dos gráficos, sem equivaler a
inspeção de pixels, responsividade real ou jornadas completas no navegador.

QA visual/E2E permanece pendente. O ambiente managed-linux não disponibilizou
`cua_repl.js`; a skill Sites orienta omitir browser QA nessa condição. Nenhum
servidor de preview ou navegador alternativo foi iniciado. A validação de build
não é apresentada como homologação visual.

## Pendências explícitas

As sete skills da Etapa 1 ainda precisam de integração completa, wrappers,
MCP, evidências e avaliações. Importação, provedores reais, fundamentos, macro,
performance TWR/MWR, diário, aprendizado, jobs, relatórios completos e recuperação
permanecem no plano. Etapas 2 e 3 dependem da conclusão validada da fundação.
O ZIP original das duas skills não foi fornecido; seu conteúdo não foi importado.

## Precisão e cobertura do primeiro fluxo

O motor `average-cost-brl/1.0.1` usa custo médio, Decimal e NUMERIC(38,16).
Uma revisão independente encontrou e corrigiu gross materializado em operações
grandes, soma de custos sob precisão ambiente e cotação anterior a um split no
mesmo dia. As regressões passam, sem testes marcados como falha esperada.
O caixa é reconhecido por data de negociação; liquidação é informativa.
Eventos entram em ordem cronológica por carteira; retificação/estorno ainda
pendentes. Avaliações são manuais, com origem/data; cotação anterior a split
fica indisponível até nova avaliação. A interface não calcula resultados.
MCP, provedor de IA, TWR/MWR e apuração tributária ainda não integrados.

## English

Stage 1 is in progress. Stages 2 and 3 have not started. This log separates
planned scope from verified delivery; no complete stage or skill is claimed yet.
