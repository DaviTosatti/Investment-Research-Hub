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
| E1.07 | CI para API/PostgreSQL e frontend, scripts de bootstrap/check e template de PR | Sintaxe Bash validada; jobs `api` e `web` passaram no GitHub, incluindo instalação limpa, migrações, 83 testes e build | [`f1ce694`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/f1ce694c9605da0e7c2e4e0541329f82f346a583), push confirmado |
| E1.08 | Instalação, arquitetura, fontes, métodos, decisões, matriz de evidências e continuidade | Links locais conferidos; original preservado por SHA-256; 23 skills, 23 páginas, 56 casos normativos e 47 requisitos transversais preservados | [`2961f63`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/2961f6338c7b26c5d4fe91b28b65b5852c5e3c4a), push confirmado |
| E1.09 | Execução solicitada pelo usuário e primeiro acesso local | PostgreSQL saudável; API e frontend iniciados; HTTP real pelo Next.js: login, sessão, painel e titulares 200, logout 204; cookie HttpOnly. Credenciais fora do Git | Commit de registro da execução; sem alteração do código do produto |
| E1.10 | Diagnóstico da aba vazia reportada pelo usuário | Login HTML e 10 arquivos JavaScript retornam 200 internamente. `sites-preview status` informa relay indisponível; ativação do navegador compartilhado exige credencial interna não provisionada. Acesso pelo usuário ainda bloqueado pela infraestrutura de visualização | Commit de diagnóstico e correção das instruções de acesso; código do produto preservado |
| E1.11 | Continuidade preparada para execução no computador do usuário | Projeto local identificado no catálogo do Codex; menu mostrado não contém reconexão. Procedimento em LOCAL_HANDOFF preserva arquivos e a branch existente; instalação/execução local ainda não realizadas | Commit de continuidade; sem alegação de acesso entregue |

## Porte Windows nativo — E1.12

Implementados os iniciadores CMD/PowerShell, runtimes portáteis, PostgreSQL
persistente, cadastro do primeiro administrador e supervisão de processos.
O [CI Windows `42142399687`](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42142399687)
passou no commit `5d09eae`: instalação limpa, caminhos com acentos/espaços,
122 testes Python, 24 web, login, ledger, idempotência, CSV, segunda instância,
reinício com dados/checksum preservados e parada pelos atalhos CMD.
Executado em Windows Server 2022 x64 e Windows PowerShell 5.1. O alvo de uso
é Windows 10/11 x64; não houve execução no computador do usuário ou QA visual.

[ZIP Windows gerado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42142399687/artifacts/13468401568),
somente arquivos versionados. SHA-256 do artefato:
`768fbba79fd7dd8df22304fb51c574219ce0ef34a85bd2bd23a9482df45cfc80`.
Runtimes/dependências são baixados na primeira execução; banco e credenciais
nunca entram no pacote. Este incremento permanece na Etapa 1.

A primeira execução Windows (`42142242711`) confirmou download, hashes e
execução dos quatro runtimes portáteis. Detectou seletores mutuamente exclusivos
do uv; o bootstrap foi corrigido para usar somente Python gerenciado, e a
execução completa seguinte passou. Commits `feat(windows)` (`051929a`) e
`fix(windows)` (`5d09eae`) enviados à branch existente.

## Verificações executadas

[Verify — execução 42142399656](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42142399656),
commit `5d09eae`: jobs `api` e `web` aprovados no Linux. O mesmo código passou
também no job Windows acima. A atualização posterior é somente documental.

| Verificação | Resultado |
| --- | --- |
| `uv run pytest -q` / Python portátil no Windows | 122 testes passaram em ambos os sistemas, incluindo 20 de integração PostgreSQL |
| `uv run ruff check apps/api packages/engines tests` | Aprovado |
| `uv run mypy` | Motor `hub_finance` aprovado em modo estrito |
| `uv run alembic upgrade head` / `uv run alembic check` | Migrações aplicadas; nenhuma divergência |
| `npm --prefix apps/web test` | 24 testes passaram |
| `npm --prefix apps/web run typecheck` / `run lint` | Tipos de rotas gerados; TypeScript e ESLint aprovados |
| `npm --prefix apps/web run build` | Build de produção aprovado |

## Próximo bloco

Continuar a Etapa 1 com correções/estornos versionados e importação guiada,
conforme [HANDOFF.md](HANDOFF.md) e o plano integral. Contrato atual:
[API_CONTRACT.md](API_CONTRACT.md). A entrega está no
[PR #1 em rascunho](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1).

## Verificação visual

O painel segue a composição FinSight/Stockly, com navegação inspirada em Chainx:
indicadores compactos, histórico amplo, alocação em rosca e tabela de posições.
Os valores vêm da API; histórico e alocação usam custo explicitamente identificado.
Os testes de renderização cobrem dados e semântica dos gráficos, sem equivaler a
inspeção de pixels, responsividade real ou jornadas completas no navegador.

QA visual/E2E permanece pendente. O ambiente managed-linux não disponibilizou
`cua_repl.js`; a skill Sites orienta omitir browser QA nessa condição. Nenhum
navegador alternativo foi iniciado. Na solicitação posterior de execução, o usuário
autorizou iniciar API/frontend para acesso direto; os serviços foram iniciados e
verificados por HTTP. A abertura do login e das credenciais no painel do Codex foi
solicitada e retornou `queued`, sem comprovar navegação ou transferência de controle.
A validação de build/HTTP não é apresentada como homologação visual.

Após a captura de tela de uma aba vazia, confirmou-se que a URL de loopback do
servidor não é um endereço acessível diretamente no Windows do usuário. O serviço
de prévia retorna `preview relay unavailable: No such file or directory`; a
ativação nativa do navegador requer autenticação que a plataforma não provisionou.
Não há ferramenta de navegador ou encaminhamento nativo disponível nesta sessão.
Não há evidência de controle entregue pela prévia remota. O pedido atual é
atendido pelo porte Windows nativo descrito em [WINDOWS.md](WINDOWS.md), sem
depender dessa visualização, de WSL ou de outro chat. Não há túnel público.

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
