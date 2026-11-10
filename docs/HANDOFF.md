# Continuidade

Atualizado em 10/11/2026 (America/Sao_Paulo).

Repositório: DaviTosatti/Investment-Research-Hub. Branch desta comparação:
`codex/auditoria-contextos-etapa-1`, baseada na main `c509cdd`.
O [PR #1](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1) foi integrado;
a fundação e os 11 contextos já estão na main. Base inicial histórica `206f494`:
somente README. O usuário exige preservação das três etapas, commit/push por
incremento e Conventional Commits. A comparação atual não implanta o produto.

O usuário solicitou explicitamente um porte Windows, pois não possui Linux.
O caminho atual é o ZIP com `Iniciar Hub.cmd`, `Parar Hub.cmd` e `Verificar Hub.cmd`;
ver [WINDOWS.md](WINDOWS.md) e [LOCAL_HANDOFF.md](LOCAL_HANDOFF.md). Não depende de
outro chat, executor local, WSL ou Docker. O código do porte e seu artefato
passaram na [execução Windows `42147690848`](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42147690848),
commit `5e047fe`. O ZIP está nos artefatos desse run (retenção de 30 dias).

Runtimes e dados ficam separados em `%LOCALAPPDATA%\InvestmentResearchHub`.
PostgreSQL 17.6 mantém o contrato Decimal existente. O primeiro administrador é
solicitado interativamente, sem reutilizar credenciais da nuvem. Todos os serviços
escutam apenas em 127.0.0.1 (PostgreSQL 54329, API 8765, interface 8766).
128 testes Python e 25 web passaram no Windows e no Linux; Ruff/mypy, migrações,
TypeScript, ESLint e build aprovados. O smoke Windows cobriu instalação limpa,
caminhos com acentos/espaços, login, operações Decimal, CSV, recusa de segunda
instância, reinício com persistência e atalhos CMD de verificação/parada.
Foi usado Windows Server 2022 x64/PowerShell 5.1. Não houve execução no PC do
usuário nem homologação visual do Windows 10/11. A documentação foi atualizada
depois da aprovação, sem alterar o código verificado.

## Estado retomável

Pedido atual: **continuar o desenvolvimento da Etapa 1**, autorizado após E1.16.
Preservar em cada CONTEXT.md tanto o inventário real quanto o roteiro das três
etapas. O relatório CONTEXT_PLAN_COMPARISON é uma fotografia histórica, não
uma instrução para apagar compromissos futuros.

E1.17 extraiu a gravação canônica; E1.18 corrigiu os contextos preservando os
roteiros; E1.19 corrigiu os hashes portáteis de skills. E1.20 entregou a API de
importação CSV/XLSX com originais privados, prévias versionadas, quarentena,
reconciliação e confirmação atômica. Leia IMPORTS.md para contratos/limites.
317 testes Python e 40 web passaram. E1.21 integra o fluxo em
`/dados#importacoes` e valida Chromium em quatro larguras, incluindo correção,
recarga, original, revisões e viewer. CI Windows integrado ainda em andamento.
Não há nova autorização pendente para trabalhar na Etapa 1.

Pedido anterior: conferir toda a Etapa 1, especialmente identidade,
ingestão/qualidade e sua ausência nas rotas. A auditoria E1.15 está em
[STAGE_1_AUDIT.md](STAGE_1_AUDIT.md), baseada no código `93aafe4` confirmado no
GitHub. Conclusão: S01/S12/S21 parciais, S02/S03/S07/S23 não iniciadas; nenhuma
skill completa. Há 14 caminhos/19 operações HTTP e cinco páginas-base parciais.
Importação CSV/XLSX, fontes reais, originais, snapshots recuperáveis,
reconciliação, quarentena e correção versionada não existem. O pedido foi de
auditoria; este incremento não implementou essas lacunas. 59 testes existentes
do motor/API passaram, 17 deles em banco de integração isolado; nenhum dado
do produto foi modificado. Consultar o inventário antes de indicar rotas de
planejamento como recursos disponíveis.

Pedido anterior: ajustar somente mensagens de erro de cadastro/login, sem
criar cadastro pessoal do usuário. E1.14 explica campos inválidos e o limite de
senha, sem exibir valores sensíveis. As credenciais fornecidas no chat não devem
ser reproduzidas ou incorporadas ao código, documentação ou testes. Regras e
fluxo do cadastro foram mantidos. Nove testes específicos e 25 web passaram;
o CI Windows `42147690848` confirmou o incremento com 128 testes Python,
25 web e execução completa. Nenhum cadastro pessoal foi criado nesta tarefa.

O usuário abriu o iniciador no próprio Windows: sua captura confirmou PostgreSQL
iniciado e o pedido de primeiro administrador, mas os rótulos de entrada não
apareciam. E1.13 remove `Out-Host` do processo nativo e imprime campos completos
antes de `input()`. Foi orientado a digitar e-mail, nome, senha e confirmação,
pressionando Enter após cada campo. Quatro testes de cadastro passaram; o CI
nativo confirmou os campos visíveis antes da digitação e a limpeza ao cancelar.
Não pedir a senha pelo chat nem orientar recriação do banco ou da conta.

Etapa 1 em implementação, Etapas 2/3 não iniciadas; nenhuma skill completa.
Leia STATUS, IMPLEMENTATION_PLAN, REQUIREMENTS_MATRIX e API_CONTRACT. O original
integral está em `reference/Promptx.txt`, SHA-256
`d622ff865a63c4716b216bf1b590841209ce4ad7741940e61a303a577918bd2a`.

O usuário também forneceu onze referências visuais aprovadas. Elas foram
examinadas no chat e descritas em VISUAL_REFERENCES: FinSight/Stockly orientam
o dashboard; Chainx, a sidebar; as telas técnicas orientam as etapas pertinentes.

Existe monólito modular: FastAPI/SQLAlchemy/Alembic/PostgreSQL, motor Decimal e
Next.js/React/TypeScript. Login privado e papéis, titulares separados, contas e
carteiras, ativos/listagens, eventos, lançamentos imutáveis/balanceados, snapshots
manuais de preço, consulta com filtros, histórico a custo e CSV foram implementados.
Consulte STATUS para evidências de código/build e o limite de revisão visual.

Migrações até `c47fb0c93e44` (fontes, originais, lotes, prévias e recibos). Motor `average-cost-brl/1.0.1`; escala
NUMERIC(38,16), contexto Decimal 50, caixa BRL half-even. Bruto calculado pelo
motor; nenhum float no ledger. Por carteira, gravação usa lock antes de ler
idempotência e saldo. Leitura de painel/CSV usa transação repeatable-read.
Avaliações anteriores a split, inclusive no mesmo dia, ficam indisponíveis.

Limites explícitos: BRL, caixa por negociação, eventos cronológicos, até 20 mil
eventos por consulta/carteira, avaliações manuais, sem TWR/MWR. Histórico é
reconstrução econômica com revisões hoje conhecidas, não backtest point-in-time.
Consulta possui checksum; análises/snapshots persistidos completos ainda pendentes.
O ZIP original de S01/S02 não estava disponível e não foi importado.

## Próximo bloco da Etapa 1

1. Retificação/estorno versionado e reconciliação dos eventos, preservando trilha,
   custo histórico e leitura das carteiras. Completar tratamento dos eventos da
   cobertura inicial, incluindo transferências/câmbio quando suportados.
2. Expandir o importador CSV/XLSX entregue em E1.20, preservando original,
   mapeamento/prévias e decisões de duplicatas. A cobertura atual é síncrona e
   limitada. Operações extensas exigem job durável e worker único antes de serem
   aceitas em segundo plano; não simular processamento assíncrono.
3. Fontes reais e snapshots com disponibilidade histórica, fundamentos, macro,
   diário e aprendizado; completar S01/S02/S12/S03/S07/S21/S23 com wrappers/MCP,
   relatórios, performance e avaliações. Seguir dependências do plano integral.
4. Medir carga representativa, testar restauração em banco/armazenamento vazio e
   concluir revisão visual/jornadas. Só então avaliar os portões da Etapa 1.

## Ambiente e verificações

No Windows, o caminho principal é o iniciador portátil descrito acima. Ele
prepara uv 0.13.4, Python 3.12.14, PostgreSQL 17.6 e Node 24.22.1/npm 11.9.0,
com lockfiles e hashes de downloads. O workflow `.github/workflows/windows.yml`
usa instalação limpa, testa a execução e publica apenas arquivos versionados.
O Linux/Docker continua como alternativa de desenvolvimento; `scripts/check.sh`
e `.github/workflows/verify.yml` verificam esse caminho. O run Linux
`42147690624` passou no mesmo commit do porte Windows aprovado.

Testes de integração usam bancos temporários exclusivos. As operações usadas
pelo smoke Windows são sintéticas e ficam apenas no runner descartável; nenhuma
conta, senha, sessão, banco ou dependência instalada foi incluída no ZIP.

A tentativa anterior de acesso remoto teve API/frontend saudáveis, mas a prévia
do Codex indisponível. O porte Windows remove essa dependência. Não orientar
reconexão nem repetir localhost remoto como endereço acessível no PC do usuário.
A conta criada naquela nuvem pertence somente à instalação remota; suas
credenciais permanecem em `data/local-access.json`, ignorado pelo Git. Não
reproduzir esse conteúdo em logs, PRs ou no pacote Windows, nem redefinir a conta.
Antes de mexer na execução da nuvem, conferir seus processos e preservar os dados.

E1.21 executou Chromium headless e examinou capturas do fluxo de importação em
desktop/mobile; quatro larguras e papéis foram conferidos com dados sintéticos.
A indisponibilidade anterior do navegador compartilhado é histórica. A revisão
completa do produto continua pendente; o Windows do usuário não foi controlado.

English: continue Stage 1 from the actual code and evidence. The initial portfolio
slice exists, but full skills and stage gates remain incomplete. Next work is
versioned corrections and guided imports with durable jobs, followed by the
remaining foundation capabilities. Commit and push each verified increment.
