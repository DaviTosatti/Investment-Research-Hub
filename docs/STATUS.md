# Progresso verificável

Atualização: 05/11/2026 — America/Sao_Paulo.

## Estado do produto

| Etapa | Estado | Evidência atual |
| --- | --- | --- |
| 1 — Fundação, experiência visual, dados e acompanhamento | Em implementação | Inventário e contrato inicial documentados; código em construção |
| 2 — Análise avançada, classes de ativos e estratégias | Não iniciada | Escopo preservado no plano e na matriz |
| 3 — Comitê IA, colaboração, monitoramento e operação completa | Não iniciada | Escopo preservado no plano e na matriz |

Nenhuma etapa ou skill completa foi validada neste ponto.

## Registro de entregas

| Incremento | Mudança | Validação | Publicação |
| --- | --- | --- | --- |
| E1.01 | Inventário, referência integral, plano, matriz e padrão de commits | SHA-256 do original preservado; 23 skills, 23 páginas e exatamente 3 etapas conferidas | [`a198336`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/a1983363773ce1a10be280e6cbad9744fa208705), push confirmado |
| E1.02 | Motor de eventos Decimal, lançamentos balanceados e ambiente Python/PostgreSQL | 10 testes de domínio, incluindo propriedades com Hypothesis; mypy sem erros; PostgreSQL 17.6 iniciado | Commit que adiciona o motor; confirmação remota no histórico da branch |
| E1.03 | API autenticada, papéis, titulares separados, contas/carteiras, ativos/listagens, eventos imutáveis, avaliações, painel e CSV | 50 testes passaram (42 domínio/revisão e 8 integração PostgreSQL); concorrência, falta de caixa, isolamento por titular, sessão, origem e persistência; Alembic sem divergência | Commit que adiciona a API e suas evidências |

## Em implementação

Integração da interface Next.js à API já testada, revisão dos formulários,
tipos, build e documentação de instalação.
Contrato de integração: [API_CONTRACT.md](API_CONTRACT.md).

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
