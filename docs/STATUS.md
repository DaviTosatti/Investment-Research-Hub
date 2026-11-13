# Progresso verificável

Atualização: 12/11/2026 — America/Sao_Paulo.

## Estado do produto

| Etapa | Estado | Evidência atual |
| --- | --- | --- |
| 1 — Fundação, experiência visual, dados e acompanhamento | Em implementação | Primeiro fluxo de carteiras integrado; motor e API verificados; requisitos restantes preservados |
| 2 — Análise avançada, classes de ativos e estratégias | Não iniciada | Escopo preservado no plano e na matriz |
| 3 — Comitê IA, colaboração, monitoramento e operação completa | Não iniciada | Escopo preservado no plano e na matriz |

Nenhuma etapa ou skill completa foi validada neste ponto.

## Repasse para colegas e padronização de PR — E1.24

Pedido: um MD para compartilhar o contexto do chat/projeto com colegas e seus
GPTs, incluindo normas de PR para aprovação de Davi. Entregue
[CONTEXTO_PARA_COLABORADORES.md](CONTEXTO_PARA_COLABORADORES.md): histórico das
decisões, base `e54b6d5` e código validado `02eaddb`, arquitetura, cobertura real,
limites, rotas de ingestão, Windows, leitura de contexto e os três roteiros.
A consulta ao GitHub confirmou PR #3 aberto/em rascunho, ainda sem merge.

CONTRIBUTING/AGENTS e o template de PR alinham branches por tarefa, dependências,
Conventional Commits, passos de conferência, ambiente/comandos/resultados/SHA,
CI, migrações/recuperação e aprovação final por `DaviTosatti`. Contextos de docs
e .github atualizados preservando as três etapas. Não há `.codex/` versionado
nesta cópia; o repasse explica onde o contexto realmente reside.

Validação documental: script Python conferiu **38 links locais**, 23 skills na
divisão 7/12/4, preservação dos três roteiros nos dois contextos alterados,
existência dos pontos de entrada citados e fechamento de blocos de código.
Campos do template/diff revisados; `git diff --check` aprovado.
Resultados de 318 testes Python/40 web pertencem ao código de E1.23; não são
uma nova execução deste incremento. Sem mudança funcional, configuração de
permissões/proteções remotas, convites, merge ou implantação.

## Incremento de ingestão aprovado no Windows e Linux — E1.23

Código validado: [`02eaddb`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/02eaddb698fc1e6320f603b702d895be2762b31c).
[CI Linux `42911482596`](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482596)
e [CI Windows `42911482586`](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482586)
aprovados. **318 testes Python e 40 web**, lint, tipagem configurada, migrações,
build e integridade das 26 skills. A correção E1.22 passou no Windows real.

O smoke nativo confirmou instalação limpa com espaços/acentos, login, precisão
Decimal, importação pelo frontend, download do original, recibo e confirmação
idempotente após parar/reiniciar, recusa de segunda instância e atalhos CMD.
Windows Server 2022 x64/PowerShell 5.1; sem controlar o computador do usuário.
O fluxo de UI foi verificado separadamente em Chromium Linux em E1.21.

[Pacote Windows validado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482586/artifacts/13808241171):
`Investment-Research-Hub-Windows-x64`, 1.116.417 bytes, retenção até 10/12/2026.
SHA-256 do artefato informado pelo GitHub:
`85dd835ed01b589a2b3d76c3b7b797a90df028759beea3956c18c88dbb94d5e1`.
Contém somente arquivos versionados; sem bancos, contas pessoais ou segredos.
Este registro posterior altera documentação; não altera o código validado.

Usar **Dados e auditoria → Importar operações**. [Contrato](IMPORTS.md).
Etapa 1 permanece parcial: provedores externos, identidade oficial/histórica,
retificação de lançamentos, jobs, demais módulos e portões ainda pendentes.
Etapas 2/3 preservadas. Ambiente sintético de QA encerrado; dados do produto
preservados. Os 11 contextos mantêm o inventário real e as três etapas.

## Validação portátil de nomes internos XLSX — E1.22

O CI Linux `42910689572` aprovou API e web no commit `6234ee8`. O Windows
`42910689317` instalou os runtimes, compilou o frontend e aprovou o check de
skills, mas encontrou uma falha entre os 317 testes: o construtor `ZipInfo` no
Windows normalizava a barra invertida usada pelo arquivo de teste. O mesmo
comportamento de leitura também ocultava o nome original na validação.

O parser agora valida `orig_filename`, antes da normalização de barras e NUL.
A construção dos ZIPs sintéticos conserva os nomes malformados byte a byte em
ambos os sistemas. Acrescentado caso com NUL; não há extração de membros ZIP.
Validação local dirigida: **151 testes** do parser/integração XLSX passaram,
com Ruff aprovado. O CI nativo será repetido antes de indicar o novo pacote.

## Interface integrada e jornada de importação — E1.21

Disponível em **Dados e auditoria → Importar operações** (`/dados#importacoes`),
com acesso também por Operações. Seleção de carteira/titular e fonte, modelo CSV,
upload, amostra, mapeamento, formatos, prévia, correção com motivo, decisões de
reconciliação, confirmação, recibos, download e histórico de revisões. Dados de
carteira continuam calculados pela API. Interface PT/EN no padrão visual existente.

Validação: **40 testes web**, typecheck, ESLint e build Next.js passaram. Chromium
executou o build de produção com PostgreSQL exclusivo e contas sintéticas:
login, upload, linha nula em quarentena, correção justificada, nova prévia,
confirmação, download byte a byte, recarga e reenvio idempotente. Revisão antiga
ficou somente para consulta; viewer consultou histórico e teve escrita recusada.
Sem erros JavaScript nessas jornadas. Larguras 1440/1024/768/390 sem overflow do
documento; capturas desktop/mobile examinadas. Isso valida o recorte de ingestão,
não a homologação de todas as páginas/jornadas da Etapa 1 nem o PC do usuário.

Teste nativo Windows e novo pacote aprovados posteriormente em E1.23.
O ambiente de QA é temporário e separado dos dados do produto; nenhum cadastro
pessoal, credencial de teste, extrato ou banco foi incluído no Git.

## Ingestão de operações com evidência e reconciliação — E1.20

Entregues serviços e rotas reais de upload CSV/XLSX, fontes de arquivos,
originais privados em PostgreSQL, snapshots de prévias, qualidade e linhagem.
Mapeamento de colunas, nulos preservados, formatos/unidades explícitos, revisões
com motivo, quarentena, decisões de possíveis duplicatas e confirmação atômica
via motor compartilhado. [Contrato completo e limites](IMPORTS.md).

24 caminhos/31 operações HTTP, incluindo `/sources`, `/imports`, `/snapshots`,
`/quality`, `/lineage`. Reimportação idêntica reutiliza o lote; referências da
mesma fonte/carteira reconciliam entre arquivos; concorrência e prévias obsoletas
não duplicam lançamentos. Candidatos sem identidade suficiente exigem decisão.
Identificação numérica XLSX é normalizada sem float; liquidação/encargos ausentes
não comprovam uma execução distinta; referências retornadas são limitadas.

Validação local: **317 testes Python passaram** (145 do parser, 44 de integração
específicos da ingestão e 128 preexistentes), Ruff, mypy do motor, Alembic sem
operações pendentes e integridade das 26 skills. A migração acrescenta tabelas e
triggers append-only, preservando a base existente. Testes usam bancos exclusivos.
O smoke Windows foi ampliado para upload pelo frontend e preservação de original,
recibo e idempotência após reinício; execução nativa do incremento aprovada posteriormente em E1.23.

Limites: até 2 MiB/500 linhas/40 colunas, processamento síncrono; sem alegar jobs.
São fontes de arquivos enviados, não provedores externos. Correções entregues são
anteriores ao lançamento; retificação de operações confirmadas, identidade oficial,
fontes externas e demais portões da Etapa 1 permanecem pendentes. A interface é
registrada separadamente em E1.21; nenhuma etapa/skill foi declarada concluída.

## Integridade de skills igual no Windows e Linux — E1.19

Identificada a causa dos cinco hashes divergentes: `sorted(Path)` usa ordenação
sem distinção de caixa no Windows e com distinção no Linux. Ordenação por
`relative_path.casefold()` reproduziu os 26 hashes antigos; somente as cinco
skills com múltiplos arquivos mudavam na ordem POSIX.

O sincronizador agora ordena explicitamente pelo caminho relativo POSIX em
ambos os sistemas. Regenerados apenas os cinco `computedHash`; nenhum conteúdo,
espelho, origem ou commit de skill foi alterado. Check local: `26 skills; ok`.
Incluído check nos workflows Linux/Windows e em `scripts/check.sh`; validação
nos runners será registrada após a execução do CI do incremento integrado.

## Contextos alinhados sem apagar o roteiro — E1.18

Corrigidos os 11 CONTEXT.md com base no código: tecnologias, nomes de tipos,
comandos, permissões do grupo, comportamento do motor e critérios de teste.
Preservadas as seções do que existe, contratos/invariantes e as três etapas em
cada diretório. Requisitos omitidos da Etapa 1 foram acrescentados ao roteiro,
incluindo fontes/ingestão, pesquisa, aprendizado, jobs, recuperação e baseline.
Nenhuma funcionalidade futura foi marcada como implementada.

Validação documental: estrutura dos 11 arquivos, 33 entradas de etapas ainda
pendentes, 115 links locais resolvidos e ausência de erros de whitespace.
O lockfile de skills ainda tem cinco hashes divergentes; a causa segue em análise.

## Retomada autorizada e gravação compartilhada — E1.17

O usuário autorizou continuar a Etapa 1 após o relatório. Os roteiros das três
etapas nos CONTEXT.md serão preservados, distinguindo código existente de entregas
futuras. A pausa indicada em E1.16 é histórica e foi encerrada por essa autorização.

Extraída a gravação de eventos para `hub_api.transaction_service`, reutilizável
por operações manuais e pelo importador em desenvolvimento. Mantidos lock por
carteira, idempotência, validação cronológica e motor Decimal. Importações ainda
não são declaradas entregues neste incremento.

Validação: Ruff nos dois arquivos alterados e 15 testes PostgreSQL de carteiras,
idempotência, concorrência e regressões passaram em banco temporário exclusivo.

## Comparação de contextos com o plano — E1.16

O usuário pediu a comparação de cada `CONTEXT.md` antes de autorizar a
continuação do desenvolvimento. [Relatório](CONTEXT_PLAN_COMPARISON.md)
baseado em `main` `c509cdd`, com os 11 contextos adicionados após a auditoria
anterior. O arquivo mestre é `docs/IMPLEMENTATION_PLAN.md`.

Resultado: escopo de três etapas preservado, mas há contratos/tecnologias
incorretos e omissões nos roteiros locais. Ingestão continua não implementada;
OpenAPI mantém 14 caminhos/19 operações. Nenhuma mudança no código de apps,
motor ou testes desde `44b2265`; contextos não concluíram funcionalidades.

Verificações: 21 links locais válidos; 25 testes web passaram; mypy configurado
para o motor passou. O comando documentado `mypy apps/api/src` retornou 136
erros em sete arquivos. `sync_agent_skills.py --check` falhou por cinco hashes
divergentes no lockfile. Falhas registradas, sem correção silenciosa ou alegação
de aprovação. Não houve execução de migrações nem alteração dos dados.

Este incremento publica somente relatório e continuidade. A autorização para retomar foi recebida posteriormente em E1.17.
Etapas 2 e 3 permanecem não iniciadas. A fundação e os contextos anteriores já
estão integrados à main; o estado de PR em rascunho nos registros antigos é histórico.

## Auditoria da cobertura da Etapa 1 — E1.15

A [auditoria funcional de 10/11/2026](STAGE_1_AUDIT.md) confrontou o prompt,
o plano e a matriz com o código `93aafe4`, confirmado na branch remota.
**Etapa 1 incompleta:** S01/S12/S21 parciais; S02/S03/S07/S23 não iniciadas.
Identidade, ingestão e qualidade têm somente a base de ativos, avaliações
manuais, idempotência de eventos e trilha de ações. Importador CSV/XLSX,
provedores reais, originais de arquivos, snapshots recuperáveis, quarentena,
reconciliação e correções versionadas ainda não estão implementados.

Inventário executado: 14 caminhos/19 operações HTTP e cinco das doze páginas-base
parcialmente implementadas. Vinte caminhos planejados, incluindo `/imports`,
`/sources`, `/snapshots`, `/quality` e `/lineage`, retornaram 404 em GET e POST.
O `snapshot_id` atual é checksum da consulta; o CSV é exportação de posições.
59 testes existentes de motor/API passaram, incluindo 17 de integração em
banco temporário. Isso não comprova os fluxos ausentes. Build web, execução
Windows e QA visual não foram repetidos nesta auditoria documental.

Entrega deste incremento: relatório com evidências, inventário de rotas,
cobertura das sete skills/páginas e portões pendentes. Nenhum módulo ausente
foi marcado como entregue; Etapas 2 e 3 permanecem não iniciadas.

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
O [CI Windows `42143415705`](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42143415705)
passou no commit `141a339`: instalação limpa, caminhos com acentos/espaços,
122 testes Python, 24 web, login, ledger, idempotência, CSV, segunda instância,
reinício com dados/checksum preservados e parada pelos atalhos CMD.
Executado em Windows Server 2022 x64 e Windows PowerShell 5.1. O alvo de uso
é Windows 10/11 x64; não houve execução no computador do usuário ou QA visual.

[ZIP Windows gerado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42143415705/artifacts/13469510859),
somente arquivos versionados. SHA-256 do artefato:
`ee4a5b018df27e6629cc9a4a54ae9e7dc97bd3851b5bd7d9d3e4b5e11aea1840`.
Runtimes/dependências são baixados na primeira execução; banco e credenciais
nunca entram no pacote. Este incremento permanece na Etapa 1.

A primeira execução Windows (`42142242711`) confirmou download, hashes e
execução dos quatro runtimes portáteis. Detectou seletores mutuamente exclusivos
do uv; o bootstrap foi corrigido para usar somente Python gerenciado, e a
execução completa seguinte passou. Commits `feat(windows)` (`051929a`) e
`fix(windows)` (`5d09eae`) enviados à branch existente.

Revisão de distribuição: a árvore opcional do pgAdmin chega a 170 caracteres
dentro do ZIP PostgreSQL e pode exceder o limite clássico de caminhos ao somar
LocalAppData/staging. O extrator agora mantém somente `bin`, `lib`, `share` e
avisos da raiz. O CI passa a usar o diretório real padrão em LocalAppData para
runtimes/dados. A instalação limpa e todos os testes passaram nessa configuração
no run `42143415705`, commit `141a339`. O maior caminho interno dos componentes
do servidor tem 62 caracteres, contra 170 da árvore opcional removida.

## Primeiro acesso no console — E1.13

A captura do usuário mostrou o servidor iniciado e a mensagem de criação do
administrador, mas sem o rótulo do campo aguardando entrada. O encaminhamento
`Out-Host` do PowerShell retinha prompts sem quebra de linha. O iniciador agora
preserva a saída nativa; a CLI mostra instruções e os rótulos de e-mail/nome em
linhas completas, com flush antes de aguardar digitação. Senhas continuam ocultas.

Quatro testes de cadastro passaram no Linux e Ruff aprovou os arquivos alterados.
O smoke Windows foi ampliado para iniciar o fluxo interativo, aguardar o campo
antes de fornecer e-mail e conferir o próximo campo antes de cancelar por EOF,
sem criar conta ou perder dados. O [CI Windows 42145542854](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42145542854)
passou no commit `4d1ddaf`, incluindo `WINDOWS FIRST ACCESS PASS`, 123 testes
Python, 24 web e o smoke completo de uso/reinício. O [Verify Linux](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42145544086)
também passou. [ZIP corrigido](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42145542854/artifacts/13469499679).
SHA-256: `936811df360c60ec2504430cd7efd99a4d0d11cdf5c9fdaf2d1e4e7e334da48d`.
A validação anterior executava o bootstrap sem interação e não detectava esse
problema de exibição. Contas existentes e dados financeiros não foram alterados.

## Mensagens de cadastro e login — E1.14

O usuário limitou o ajuste às mensagens de erro, sem cadastrar seus dados.
O console agora informa o motivo da rejeição: e-mail inválido, senha muito curta
(com quantidade recebida e mínimo exigido), senha longa, nome inválido ou
confirmação diferente. Não imprime a senha. A API de login/membros usa mensagens
legíveis de validação; credenciais incorretas continuam com o mesmo erro de
autenticação. A interface já exibe essas mensagens no formulário.

Nove testes específicos de cadastro/autenticação e 25 testes web passaram;
Ruff aprovado. As verificações usam somente contas sintéticas em bancos de teste
isolados. Nenhum dado fornecido no chat foi inserido no produto ou nos arquivos.
Regras de senha, autenticação e fluxo de cadastro permanecem os mesmos.
O [CI Windows 42147690848](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848)
passou no commit `5e047fe`: 128 testes Python, 25 web e smoke de primeiro acesso,
login, operações, CSV, persistência e encerramento. O [Verify Linux](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690624)
também passou. [ZIP atualizado](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848/artifacts/13470653605).
SHA-256: `b992d86f3d4b20413bde925a7f73796888a7b732e94df5ef2bc5b598ba27446e`.

## Verificações executadas

[Verify — execução 42147690624](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690624),
commit `5e047fe`: jobs `api` e `web` aprovados no Linux. O mesmo código passou
também no job Windows acima. A atualização posterior é somente documental.

| Verificação | Resultado |
| --- | --- |
| `uv run pytest -q` / Python portátil no Windows | 128 testes passaram em ambos os sistemas, incluindo 26 de integração PostgreSQL |
| `uv run ruff check apps/api packages/engines tests` | Aprovado |
| `uv run mypy` | Motor `hub_finance` aprovado em modo estrito |
| `uv run alembic upgrade head` / `uv run alembic check` | Migrações aplicadas; nenhuma divergência |
| `npm --prefix apps/web test` | 25 testes passaram |
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
