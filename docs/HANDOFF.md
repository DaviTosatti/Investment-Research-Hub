# Continuidade

Atualizado em 05/11/2026 (America/Sao_Paulo).

Repositório: DaviTosatti/Investment-Research-Hub. Branch: `codex/etapa-1-fundacao`.
[PR #1](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1) em rascunho.
Base inicial `206f494`: somente README. Usuário autorizou iniciar o produto,
exigiu leitura cuidadosa do anexo e preservação das três etapas, com commit/push
por incremento e Conventional Commits. Não houve merge na main nem implantação.

Para a solicitação atual de abrir/utilizar o programa no computador do usuário,
seguir [LOCAL_HANDOFF.md](LOCAL_HANDOFF.md). O projeto local foi localizado pelo
Codex; sua execução depende de abrir um chat com executor local. A sessão remota
não disponibiliza ferramenta para transferir a tarefa automaticamente. O menu
de conversa mostrado pelo usuário não contém reconexão; não repetir essa orientação.

## Estado retomável

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

Migrações até `0002_ledger_integrity`. Motor `average-cost-brl/1.0.1`; escala
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
2. Importador CSV/XLSX com original preservado, mapeamento/prévia, decisões de
   duplicatas entre arquivos e concorrência. Operações extensas exigem job durável
   e worker único antes de serem aceitas em segundo plano.
3. Fontes reais e snapshots com disponibilidade histórica, fundamentos, macro,
   diário e aprendizado; completar S01/S02/S12/S03/S07/S21/S23 com wrappers/MCP,
   relatórios, performance e avaliações. Seguir dependências do plano integral.
4. Medir carga representativa, testar restauração em banco/armazenamento vazio e
   concluir revisão visual/jornadas. Só então avaliar os portões da Etapa 1.

## Ambiente e verificações

Veja o README para bootstrap, primeiro administrador e execução local. O banco
Docker usa volume persistente; `.env` e dados são ignorados pelo Git. Nenhum
administrador com senha padrão ou dado demonstrativo foi inserido no banco da aplicação.
Testes usam bancos temporários exclusivos, removidos após a execução.

Após a solicitação explícita de executar o programa, foram iniciados Uvicorn em
`127.0.0.1:8000` e Next.js de produção em `127.0.0.1:3000`. O primeiro administrador
local foi criado com senha aleatória exclusiva e evento de auditoria `bootstrap`.
As credenciais estão apenas em `data/local-access.json`, com permissão 0600 e
exclusão do Git. Não reproduzir senha, cookie ou conteúdo do arquivo em logs/PRs.
Login, sessão, dashboard, titulares e logout passaram em chamadas HTTP reais pelo
encaminhamento do Next.js. Nenhuma operação financeira foi cadastrada.

Para o usuário, a URL é `http://localhost:3000/login` no navegador do ambiente.
A abertura do navegador e do arquivo de acesso pelo painel do Codex retornou
`queued`; isso não comprova que o painel foi aberto ou que o controle foi entregue.
Antes de retomar, confira os processos/portas; não presuma que sobrevivem a uma
reinicialização do ambiente e não recrie/redefina a conta existente.

O usuário depois informou uma aba vazia, sem URL carregada. O servidor permaneceu
saudável: HTML do login com campo de senha e os 10 scripts referenciados retornaram
200. A visualização está bloqueada: `sites-preview status` não encontra o relay,
e a ativação nativa do navegador falha por credencial interna não provisionada.
O conector declara suporte a desktop remoto, mas não confirma sua prontidão;
ferramentas de navegador/encaminhamento não foram disponibilizadas. É necessário
restabelecer a visualização pelo próprio Codex. Não gerar/substituir credenciais
internas da plataforma. `localhost` no Windows não alcança este servidor remoto,
e não existe URL pública de implantação para fornecer. Não repetir o link local
como se fosse acesso externo confirmado.

Python 3.12.14, uv 0.13.4, PostgreSQL 17.6, Node 24.22.1/npm 11.9.0. Dependências
resolvidas em `uv.lock` e `apps/web/package-lock.json`. `scripts/check.sh` reúne
verificações e `.github/workflows/verify.yml` as replica no GitHub.
59 testes Python e 24 testes web passaram; Ruff/mypy, migrações, TypeScript, ESLint
e build aprovados. Os jobs `api` e `web` da execução `42133669523`, commit
`f1ce694`, passaram no GitHub. O registro completo e o link estão em STATUS;
esta atualização posterior modifica somente documentação.

O ambiente managed-linux não disponibilizou `cua_repl.js`; a skill Sites orienta
a omitir browser QA nessa condição. Não foi instalado navegador alternativo nem
declarada validação visual. A execução direta posterior foi solicitada pelo usuário;
API, frontend e PostgreSQL foram deixados ligados para seu acesso. Nenhum agente
de desenvolvimento continua trabalhando após o handoff.

English: continue Stage 1 from the actual code and evidence. The initial portfolio
slice exists, but full skills and stage gates remain incomplete. Next work is
versioned corrections and guided imports with durable jobs, followed by the
remaining foundation capabilities. Commit and push each verified increment.
