# Auditoria funcional da Etapa 1

Data: 10/11/2026. Código auditado: [`93aafe4`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/93aafe4baa316aee478a389c654be8d35ed17484),
branch `codex/etapa-1-fundacao`, [PR #1](https://github.com/DaviTosatti/Investment-Research-Hub/pull/1).
O fetch e a consulta das branches remotas confirmaram esse SHA. A `main`
continua em `206f494`, com o README inicial. Não foram examinados arquivos
privados da instalação Windows do usuário.

**Conclusão: a Etapa 1 não está completa.** Existe um primeiro fluxo integrado
de cadastro, carteiras, operações manuais, avaliações, auditoria de ações e CSV.
O bloco **Identidade, ingestão e qualidade está parcialmente implementado**:
o importador CSV/XLSX, os provedores reais e a auditoria de dados financeiros
exigidos pelo plano ainda não existem. A ausência dessas funções nas rotas
corresponde à ausência de implementação.

Das sete skills, S01/S12/S21 têm partes implementadas; S02/S03/S07/S23 não
iniciaram. **Nenhuma das sete está completa ou validada como skill.** Etapas
2 e 3 permanecem não iniciadas. Esta auditoria não adiciona uma etapa nem
transfere requisitos da fundação para etapas posteriores.

## Escopo e método

Confrontados o [prompt original](reference/Promptx.txt), §§5–6 e Etapa 1 do §8,
o [plano](IMPLEMENTATION_PLAN.md), a [matriz](REQUIREMENTS_MATRIX.md), todos os
módulos de produção, modelos/migrações, páginas Next.js e testes pertinentes.
O SHA-256 do original foi conferido e permanece
`d622ff865a63c4716b216bf1b590841209ce4ad7741940e61a303a577918bd2a`.

O inventário foi obtido de `app.openapi()` na aplicação importada do código,
não apenas da documentação. Foram encontradas **14 URLs e 19 operações HTTP**,
13 tabelas e cinco páginas funcionais do Hub, além do login e redirecionamento
da raiz. Requisições em processo com `TestClient` confirmaram 404 nos caminhos
ausentes listados abaixo, com conexão ao banco explicitamente bloqueada nessa
inspeção. Não se trata de erro de permissão de uma rota existente.

“Parcial” abaixo significa que existe código útil, mas faltam partes do requisito.
“Ausente” significa que a capacidade não foi encontrada no código auditado;
nomes de tabelas propostos, diagramas e URLs de fontes no catálogo não contam
como implementação. Os estados oficiais continuam os de STATUS.

## Identidade, ingestão e qualidade — conferência detalhada

| Requisito | Resultado | Evidência existente e lacuna |
| --- | --- | --- |
| Emissor, instrumento e listagem | Parcial | [Models](../apps/api/src/hub_api/models.py#L85) separa as três entidades por UUID/FK. [POST /instruments](../apps/api/src/hub_api/main.py#L409) cria instrumento e listagem; `issuer_name` opcional cria um emissor novo. Não há resolução/reutilização de emissor existente por identificador oficial. A UI não envia emissor. `Listing.instrument_id` é único, limitando a uma listagem por instrumento. |
| Símbolos e vigência | Parcial | `exchange`, `ticker`, `valid_from` e `valid_to` existem no modelo, mas o contrato de criação não recebe vigências e as consultas não as usam. Não há fluxo de mudança de ticker, aliases, dupla listagem ou identificadores oficiais. Não atende à identidade histórica completa de R09. |
| Fonte e tempo | Parcial | [Price](../apps/api/src/hub_api/models.py#L153) guarda preço manual, `as_of`, texto `source`, autoria, `retrieved_at` e hash. Não há catálogo persistido de fontes/documentos, URL de origem, período econômico, `published_at`, `available_at`, escala ou escopo de consolidação. Uma descrição digitada da fonte não comprova coleta. |
| Snapshots e revisões | Parcial | Avaliações são linhas imutáveis; a consulta escolhe a mais recente por data/sequência. O [snapshot_id do painel](../apps/api/src/hub_api/portfolio_service.py#L206) é SHA-256 dos IDs de eventos/preços, carteiras, data e método. Não existe entidade de snapshot persistido, manifesto completo ou recuperação de uma versão anterior pelo ID. O CSV recalcula e pode rejeitar a exportação se o checksum mudou. |
| Disponibilidade histórica | Ausente | A [seleção de preços](../apps/api/src/hub_api/portfolio_service.py#L115) filtra `as_of`, sem cutoff de publicação/disponibilidade. Uma avaliação inserida depois pode participar da reconstrução de uma data econômica anterior. É reconstrução com o conhecimento atual, não consulta do que se conhecia naquela data; T10/T11 não estão atendidos. |
| Fontes reais acessíveis | Ausente | Não há adaptador de coleta de CVM, BCB, IBGE, B3, SEC, FRED ou outro provedor de dados financeiros. O [catálogo](DATA_CATALOG.md) declara as fontes externas planejadas. **Zero integrações externas de dados financeiros implementadas/validadas**; sem cobertura, limites, atraso ou recuperação de versões demonstrados. Downloads de runtimes Windows não são provedores financeiros. |
| CSV/XLSX: upload, mapeamento e prévia | Ausente | Não há endpoint de upload, parser CSV/XLSX, mapeamento de colunas, normalização de datas/números, totalizadores, confirmação ou conciliação de importação. `/operacoes` envia eventos JSON manuais. `GET /reports/positions.csv` somente exporta posições. |
| Originais preservados | Ausente para ingestão | Não há armazenamento de arquivos financeiros originais, referência ao arquivo/linha, versão do importador ou decisões de mapeamento. `raw_payload_hash` é hash do pedido de preço validado; não guarda o conteúdo original nem permite recuperá-lo. Preservar o Promptx no repositório não atende à preservação de extratos/documentos financeiros. |
| Reimportação sequencial, concorrente e entre arquivos | Parcial apenas na API de eventos | [POST /transactions](../apps/api/src/hub_api/main.py#L488) usa lock por carteira, chave idempotente e `(portfolio_id, source, external_id)`, com conflito para conteúdo diferente. Isso protege retries JSON quando o cliente fornece a identidade. Não há identificação econômica de linhas entre arquivos, tratamento de ambiguidade ou reconciliação de duplicatas sem identificador comum. T04/T05 completos continuam pendentes. |
| Unidades, escalas e períodos | Ausente para dados importados/provedores | Decimal e BRL estão implementados no ledger; validações de quantidade/preço/data não normalizam reais versus milhares/milhões nem acumulados/trimestres/TTM. Não há fatos contábeis, conversões de escala ou regras de períodos; T08/T09 pendentes. |
| Nulos e qualidade | Parcial | [Consulta de posições](../apps/api/src/hub_api/portfolio_service.py#L141) mantém preço/mercado/resultado não realizado como `null` quando falta avaliação utilizável e invalida avaliação anterior a split. O contrato expõe `valid`, `stale`, `unavailable`, com regra de sete dias para avaliações manuais. Faltam estados incompleto/divergente/quarentena, motivos estruturados por registro, tolerâncias por grandeza e políticas por tipo de fonte. T12 tem cobertura restrita a esse fluxo. |
| Quarentena e reconciliação | Ausente | Não há entidades, regras executáveis, relatório por severidade, revisão/liberação de registros, comparação de fontes ou conciliação de extrato versus ledger. Validação 422 de um formulário não implementa quarentena. |
| Correção rastreável e impacto | Parcial apenas na trilha de ações | [AuditEvent](../apps/api/src/hub_api/models.py#L167) registra autor, ação, entidade e data. `Transaction.revision` nasce em 1; não existe encadeamento de correções/estornos nem cálculo de impacto. Eventos anteriores ao último são [recusados](../apps/api/src/hub_api/main.py#L521) com mensagem de retificação pendente. O trigger preserva imutabilidade, mas sua mensagem sobre correção versionada não oferece tal fluxo. |
| Linhagem e cobertura efetiva | Ausente | Não há vínculo original → transformação → fato → indicador/análise, reprocessamento versionado ou métricas de cobertura de provedor. A “cobertura das posições” em `/dados` mede somente presença/idade da avaliação manual nas posições do filtro. |

Uma evidência que pode causar confusão: em
[test_idempotency_and_external_identity](../tests/integration/test_portfolios.py#L93),
a variável `other_file` representa outro POST JSON com nova chave idempotente
e o mesmo `external_id`. Nenhum arquivo é aberto nesse teste. Ele comprova
reutilização da identidade externa, não importação ou reconciliação entre arquivos.

Também são capacidades distintas:

- `GET /audit`: trilha de ações de usuários; a S12 exige auditar os dados financeiros.
- `snapshot_id`: checksum da consulta; ainda não é um snapshot recuperável por versão.
- Novas linhas em `prices`: histórico de avaliações manuais; falta o envelope de revisões de fontes.
- `revision` do frontend: contador para recarregar dados; não é revisão de um documento.

## Todas as skills e blocos da Etapa 1

| Skill | Estado | Implementado | Falta para sua cobertura da Etapa 1 |
| --- | --- | --- | --- |
| S01 — Finanças Pessoais e Investimentos | Em implementação | Titulares, conta/carteira, oito tipos de evento manual, caixa/posições/custo/resultado derivados em BRL. | Importação, saldos iniciais identificados, correção/estorno, transferências/câmbio, cobertura de eventos/proventos, TWR/MWR, metas, reserva/liquidez, planejamento e cenários determinísticos. |
| S02 — Radar de Mercados | Não iniciado | Cadastro manual de ativo/preço é dependência da skill, não um radar. | Busca/contexto de mercado, watchlists, índices/câmbio, séries e provedores com atraso/lacunas identificados. |
| S12 — Auditoria de Dados Financeiros | Em implementação | Invariantes do ledger, idempotência de eventos, nulos e idade das avaliações, trilha de ações. | Importação/conciliação, documentos, envelope temporal, normalização, regras de qualidade, quarentena, revisões e linhagem do bloco acima. |
| S03 — Análise Fundamentalista | Não iniciado | Nenhum serviço de demonstrações/indicadores encontrado. | Documentos auditados, DRE/balanço/caixa, TTM, métricas e explicações setoriais apropriadas, fontes e datas. |
| S07 — Inteligência Macroeconômica | Não iniciado | Nenhum serviço/série macro encontrado. | BCB/IBGE/FRED conforme cobertura definida, séries e revisões, calendários, frequências, observado versus hipótese e cenários. |
| S21 — Relatórios e Dashboards | Em implementação | Painel e CSV básico de posições, mesmo motor/filtros e proteção por checksum. | Motor/templates de relatórios da cobertura inicial, prévia/seções, formatos previstos, histórico persistido, manifestos e artefatos autorizados. O plano amplia análises até a Etapa 3; CSV isolado não conclui a base. |
| S23 — Mentor de Investimentos | Não iniciado | Nenhum glossário, trilha ou exemplo didático executável encontrado. | Aprendizado, exercícios/histórico, explicação dos indicadores vinculada aos cálculos, fontes e avaliações didáticas. |

**Wrappers, ferramentas MCP e avaliações completas das sete skills estão
pendentes.** Não existe `SKILL.md` de negócio versionado neste repositório;
`.agents/development/README.md` descreve frentes de desenvolvimento. O ZIP
original de S01/S02 continua ausente, mas isso não impede desenvolver os
requisitos definidos no prompt.

| Bloco adicional do plano | Situação conferida |
| --- | --- |
| Inspeção e contratos | Original preservado, plano de três etapas, matriz, catálogo e decisões documentados. As tabelas de cobertura integral descrevem destino, não entrega concluída. |
| Primeiro incremento integrado | FastAPI/PostgreSQL/Alembic, Next.js, autenticação e papéis, autoria/titularidade, ledger Decimal, avaliações e CSV existem. Está limitado ao recorte descrito no contrato; QA visual completo ainda pendente. |
| Contabilidade e acompanhamento | Eventos `deposit`, `withdrawal`, `buy`, `sell`, `dividend`, `fee`, `tax`, `split`. Caixa por negociação; liquidação informativa; ordem cronológica; limite de 20 mil eventos por consulta/carteira. `summary.performance` é explicitamente `null`. Não há transferência/câmbio ou ciclo anunciado/cancelado/recebido dos proventos. |
| Pesquisa e aprendizado | Faltam os módulos S02/S03/S07/S23, diário/teses e comentários básicos. Eles pertencem à Etapa 1; não devem esperar o Comitê da Etapa 3. |
| Contratos públicos e jobs | HTTP/OpenAPI implementados no recorte manual. Sem MCP/OAuth, wrappers financeiros, fila/worker/job durável, retomada ou cancelamento de importações. Supervisão dos processos Windows não implementa jobs de domínio. |
| Operação e recuperação | Porte nativo Windows e persistência após reinício têm evidência histórica de CI. Não há rotina completa de backup/restore ou restauração validada em ambiente vazio. A orientação de copiar o banco parado não comprova esse critério. |
| Integração, motores e experiência | Motor Python possui método/versão e política Decimal, mas não manifesto completo de execução nem linha de base medida. Filtros e estado de menu ficam em memória no HubShell; não há persistência completa de preferências/rascunhos. Faltam jornadas da etapa, revisão visual/acessibilidade nas larguras previstas e avaliações das skills. |

## Rotas que existem

Inventário completo no SHA auditado. O prefixo de todas as rotas abaixo é
`/api/v1`. Definições em [main.py](../apps/api/src/hub_api/main.py#L267).

| Método | Caminho | Capacidade atual |
| --- | --- | --- |
| GET | `/health` | Banco disponível e versão da aplicação. |
| GET | `/openapi.json` | Esquema da API, exige sessão autenticada. |
| POST | `/auth/login` | Login por cookie de sessão. |
| GET | `/auth/session` | Usuário da sessão. |
| POST | `/auth/logout` | Revogação da sessão. |
| GET, POST | `/members` | Listagem de membros e criação por administrador. |
| GET, POST | `/owners` | Titulares econômicos. |
| GET, POST | `/portfolios` | Carteiras; conta criada junto com a carteira. |
| GET, POST | `/instruments` | Cadastro/listagem manual de ativos. |
| POST | `/prices` | Avaliação manual. Não há GET dedicado de histórico de preços. |
| GET, POST | `/transactions` | Lista e registro manual de eventos. |
| GET | `/dashboard` | Consulta de carteira/titular/data e avaliações disponíveis. |
| GET | `/reports/positions.csv` | Exportação básica de posições. |
| GET | `/audit` | Trilha de ações. |

Não há métodos PUT/PATCH/DELETE registrados. Essa ausência, somada aos modelos
e serviços examinados, confirma que não existe fluxo de retificação de operações.
Swagger `/docs` e ReDoc estão desativados; para inspecionar o contrato existente,
acesse `/api/v1/openapi.json` na mesma origem do site após login.

Estes **20 caminhos previstos**, sob `/api/v1`, não constam do OpenAPI e
retornaram 404 tanto em GET quanto em POST no teste de roteamento:

```text
/sources               /imports                /snapshots
/quality               /lineage                /issuers
/market                /watchlists             /analyses/fundamentals
/macro                 /learning               /theses
/comments              /decisions              /income
/events                /performance            /reports
/artifacts             /jobs
```

A existência de `/reports/positions.csv` não cria `/reports`. A tabela `issuers`
não cria `/issuers`. Contas e posições possuem cobertura embutida em carteiras
e painel; não foram consideradas ausentes apenas por não terem endpoint próprio.
Os nomes dos caminhos futuros continuam propostas de contrato, não obrigação
de criar rotas vazias para aparentar conclusão.

## Páginas da cobertura inicial

| Página prevista | Rota | Resultado |
| --- | --- | --- |
| P01 — Dashboard | `/inicio` | Existe; painel a custo/avaliações manuais, CSV. Sem performance e conteúdo dos módulos ainda ausentes. |
| P02 — Aprendizado e Mentor | `/aprender` | Ausente. |
| P03 — Mercado e watchlists | `/mercado` | Ausente. |
| P04 — Empresas | `/empresas/:instrument_id` | Ausente. |
| P08 — Macroeconomia | `/macroeconomia` | Ausente. |
| P10 — Carteiras | `/carteiras` | Existe parcialmente; faltam performance, transferências e planejamento. |
| P11 — Operações/importação | `/operacoes` | Existe apenas o fluxo manual de operações/cadastro de ativo. |
| P12 — Proventos | `/proventos` | Ausente; evento manual `dividend` não implementa a página/ciclo de proventos. |
| P19 — Diário/teses | `/diario` | Ausente. |
| P21 — Relatórios/histórico | `/relatorios` | Ausente; CSV acessível no dashboard. |
| P22 — Dados/auditoria | `/dados` | Existe para avaliações manuais e ações; sem importações, fontes, quarentena ou linhagem. |
| P23 — Administração/automações | `/administracao` | Existe para membros/saúde; sem integrações, jobs, backups ou restauração. |

Há cinco das doze páginas-base implementadas parcialmente; sete não têm rota.
A conclusão decorre da árvore `apps/web/src/app` e da navegação registrada em
[HubShell](../apps/web/src/components/hub-shell.tsx#L14). Login e raiz são páginas
de acesso e não substituem as páginas de negócio faltantes.

## Portões de conclusão do prompt

| Critério | Resultado |
| --- | --- |
| Dois usuários compartilham dados permitidos, com autoria/titularidade distintas | Coberto no recorte API do grupo privado; testes de papéis, sessão, compartilhamento e filtros passaram. Jornada completa de duas pessoas no navegador não foi demonstrada nesta auditoria. |
| Importação reconstrói posições e caixa sem duplicatas | Não atendido: importador ausente. |
| Pesquisar empresa, auditar documentos e explicar indicadores pelo Mentor | Não atendido: serviços, páginas e skills ausentes. |
| Operação aparece na carteira/histórico sem enviar ordem | Atendido no recorte dos oito eventos manuais suportados; testes executados. |
| Dashboard, performance e relatório usam mesmos cálculos/filtros | Parcial: painel/CSV compartilham serviço; performance e relatórios completos faltam. |
| Dados e preferências sobrevivem ao reinício; backup recuperável | Parcial: reinício com dados possui evidência anterior de CI Windows; preferências completas e restauração comprovada faltam. |
| Sete skills com procedimentos, ferramentas e avaliações | Não atendido. |
| Motores identificados e política numérica; wrappers/API/relatórios equivalentes | Parcial: método Decimal e versão existem; manifesto, wrappers, MCP e demais interfaces faltam. |
| Linha de base com medições reais | Não atendido: [PERFORMANCE_BASELINE](PERFORMANCE_BASELINE.md) contém protocolo e cargas propostos, sem benchmark medido. |

## Verificação executada nesta auditoria

- Fetch/consulta de branches remotas; conferência de SHA e árvore limpa inicial.
- Leitura de implementação, migrações, contratos, páginas e testes; integridade
  SHA-256 do prompt original.
- Geração do OpenAPI em memória: 14 caminhos, 19 operações; 40 requisições a
  caminhos ausentes, todas 404. Essa inspeção não conectou ao banco.
- **59 testes existentes passaram em 8,05 s**, incluindo 17 testes de integração
  em PostgreSQL e os testes do motor/revisões. A fixture cria banco temporário
  exclusivo e o remove ao final; dados do produto não foram alterados.

```sh
.venv/bin/pytest -q \
  tests/unit/test_ledger.py \
  tests/unit/test_ledger_adversarial.py \
  tests/integration/test_portfolios.py \
  tests/integration/test_contracts.py \
  tests/integration/test_review_regressions.py
```

A suíte emite um aviso de depreciação do transporte httpx do TestClient; não
houve falhas. Ela verifica o recorte existente, não valida módulos ausentes.
Testes T04/T05 de importação de arquivos, T08–T11 de normalização/disponibilidade,
T32 de reinício de job, T36 de restauração e T45 de correção/reexportação não
foram executados como jornadas completas porque esses fluxos não existem.

Não foram reexecutados build web, CI Windows ou QA visual nesta auditoria
documental. A evidência histórica desses checks continua em STATUS; os 128
testes Python/25 web do incremento anterior não significam 128 requisitos da
Etapa 1 concluídos. Nenhum provedor externo foi validado por uma consulta real.

## Ordem de continuidade dentro da Etapa 1

1. Completar identidade, envelope de fonte/tempo e armazenamento imutável de
   originais/snapshots; definir correção/estorno e reconciliação rastreáveis.
2. Implementar o importador CSV/XLSX completo, com prévia/confirmar, duplicatas
   sequenciais/concorrentes/entre arquivos e testes T04/T05/T45. Se houver
   execução em segundo plano, entregar antes o mecanismo durável de jobs,
   worker e retomada, sem aceitar trabalhos que possam desaparecer.
3. Conectar fontes reais com cobertura demonstrada; qualidade/quarentena e
   linhagem; concluir fundamentos, mercado, macro, aprendizado e diário.
4. Completar contabilidade/performance/proventos da cobertura, relatórios,
   wrappers/MCP e avaliações das sete skills; medir carga, restaurar backup
   em ambiente vazio e validar as jornadas/páginas da etapa.

O fechamento depende desses resultados verificáveis, não da quantidade de
commits, testes ou rotas criadas. Esta entrega registra a auditoria; não
implementa as funcionalidades ausentes.
