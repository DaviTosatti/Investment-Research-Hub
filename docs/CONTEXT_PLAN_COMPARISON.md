# Comparação dos CONTEXT.md com o plano de implementação

Data: 10/11/2026. Revisão solicitada antes de autorizar a continuação da Etapa 1.
Base examinada: [`c509cdd`](https://github.com/DaviTosatti/Investment-Research-Hub/commit/c509cdd9705be6bd78220289be18704a62233c50),
`main` remota. Os contextos chegaram nos commits `80d45b9`, `e8e96e7` e
`d6e8a68`, posteriores à auditoria anterior. O PR #1 já está integrado;
a informação de que a main só tinha README pertence ao registro anterior.

O arquivo do projeto correspondente ao `implementation.md` mencionado pelo
usuário é [docs/IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md). Não há arquivo
literal `implementation.md` ou `implemetation.md` nessa árvore.

**Conclusão: os 11 CONTEXT.md não demonstram conclusão da Etapa 1.** Todos
mantêm seus roteiros das três etapas desmarcados. Além das lacunas funcionais
já identificadas, existem contratos incorretos, descrições de recursos que
não existem e requisitos da Etapa 1 pouco representados nos roteiros locais.
Os contextos precisam de alinhamento antes de servirem como instrução confiável
para continuar a implementação.

Esta entrega registra o relatório e a continuidade. Não corrige os contextos,
o lockfile ou o produto. A continuação do desenvolvimento aguarda autorização
expressa do usuário, conforme seu pedido.

## Método e limites da comparação

Foram lidos integralmente os 11 arquivos `CONTEXT.md` versionados, incluindo
pastas ocultas, e a metodologia ICM. A comparação usa três níveis de evidência:

1. [Plano](IMPLEMENTATION_PLAN.md), [matriz](REQUIREMENTS_MATRIX.md) e
   [Promptx](reference/Promptx.txt): requisitos e etapas obrigatórios.
2. Contextos: inventário declarado, contratos, invariantes e pendências locais.
3. Código, modelos, workflows e comandos realmente executados: o que existe.

Uma regra ou saída desejada não comprova implementação. Um item `[ ]` no
roteiro é corretamente uma pendência. Um item `[x]`, um comando de verificação
ou um contrato apresentado como atual precisa corresponder ao código. Um
resumo local pode omitir detalhes, mas não substituir os critérios do plano.

A comparação Git com `44b2265` confirmou que não houve alteração no código
da aplicação, motor ou testes desde a auditoria anterior: nessas áreas só
entraram arquivos `CONTEXT.md`. Entraram também ferramentas de desenvolvimento
e um sincronizador de skills, que não implementam módulos financeiros.

## Conferência por diretório — todos os 11 arquivos

| Contexto examinado | Concordância com o plano | Divergências ou limites encontrados |
| --- | --- | --- |
| [Raiz](../CONTEXT.md) | Preserva três etapas, sete skills iniciais, doze páginas-base, dados compartilhados e backup inicial. | A regra de que **todos** os cadastros têm `owner_id` e `created_by` não corresponde aos modelos. “Bases funcionais” das skills não substitui os portões completos do plano. Referência a Tailwind não corresponde às dependências atuais. Ver F04/F06. |
| [apps](../apps/CONTEXT.md) | Mantém API/web, MCP, relatórios e jobs na Etapa 1. | Declara ausência total de cálculos em `apps`, embora o serviço de portfólio calcule avaliações e agregações. Cita Tailwind/Vitest inexistentes. Worker aparece no roteiro da Etapa 3: esclarecer que uma pasta física é opcional, mas execução durável de jobs da Etapa 1 não pode ser adiada. F02/F05/F06. |
| [apps/api](../apps/api/CONTEXT.md) | Inventário de 14 caminhos/19 operações está correto. Ingestão, importação, MCP e jobs estão desmarcados na Etapa 1. | Autorização por vínculo usuário–titular não existe. `AuditLog` e `bootstrap-admin` não são nomes atuais. `mypy apps/api/src` falha. O roteiro local não detalha serviços de mercado, fundamentos, macro, aprendizado, diário e performance exigidos nesta etapa. F01/F03/F04/F11/F13. |
| [apps/web](../apps/web/CONTEXT.md) | Cinco páginas atuais e sete páginas-base pendentes; upload/mapeamento CSV/XLSX corretamente pendente. | Next 15, Tailwind e Vitest incorretos; são Next 16.4.5, CSS próprio e `tsx --test`. Há 25 testes, não 24. P04 é descrita como `/acoes`, enquanto a matriz propõe `/empresas/:instrument_id`. Descreve paginação/polling e funções inexistentes; atribui recursos à página errada. F06/F07. |
| [packages](../packages/CONTEXT.md) | Preserva reutilização do motor, ausência de HTTP/banco no ledger e aceleração condicionada a evidência. | Exige equivalência bit a bit universal, incompatível com a política numérica do prompt. `pip install -e packages/engines` aponta para diretório sem manifesto de instalação; o empacotamento é na raiz. Roteiro local da Etapa 1 omite fundamentos, macro, aprendizado/metas e auditoria dos dados. F03/F12/F13. |
| [packages/engines](../packages/engines/CONTEXT.md) | Reconhece os oito eventos e deixa transferências, câmbio e TWR/MWR pendentes na Etapa 1. | Contrato de estado imutável/`PortfolioState` não corresponde a `LedgerState` mutável e retorno de lançamentos. Tipos de eventos reais são minúsculos; exceções citadas não existem. Hypothesis está atribuído ao arquivo errado. Linha de base aparece só na Etapa 2. Limite fiscal aparece sem a ressalva de fonte/vigência obrigatória. F02/F05/F10/F12. |
| [scripts](../scripts/CONTEXT.md) | Backup/restore e integração do check de skills permanecem pendentes na Etapa 1. | Sincronização é unidirecional, não bidirecional. `runtime.py` é um ponto de entrada de cinco linhas. Manifesto não contém Caddy nem um objeto `python` como no exemplo. Primeira linha de base aparece só na Etapa 2. F02/F08. |
| [tests](../tests/CONTEXT.md) | Exige testes reais, PostgreSQL, importação e relatórios na Etapa 1. | Descreve AsyncClient/testcontainers e Hypothesis no arquivo adversarial, diferentes do código. Atribui significados errados a T15/T21/T25. Restauração só aparece na Etapa 3 no roteiro local; faltam vários casos essenciais de ingestão/qualidade da Etapa 1. Exigência bit a bit precisa ser limitada à política aplicável. F02/F10/F12. |
| [docs](CONTEXT.md) | Reconhece o prompt como fonte primária, distingue proposta de entrega e preserva as três etapas. | O roteiro só cita linha de base na Etapa 2. Catálogo de dados e registro de modelos contêm principalmente contratos e métodos planejados, não inventário de provedores/métodos já suportados. O fechamento exige evidências de execução, além de manuais e documentos. F02/F03. |
| [.agents](../.agents/CONTEXT.md) | Distingue corretamente 26 skills de engenharia das 23 skills financeiras; sete skills de negócio continuam pendentes. | O comando que deveria retornar `26 skills; ok` retorna **exit 1**: cinco hashes do lockfile divergem. O check ainda não está no CI, como reconhecido no roteiro. Não há evidência nesta revisão de carregamento automático em todos os clientes citados. F09. |
| [.github](../.github/CONTEXT.md) | Descreve corretamente jobs API/web e workflow Windows. Checks de skills e links são pendências explícitas. | Triggers reais não filtram branches, ao contrário do texto. Credenciais de teste nem sempre são geradas em memória: há valores sintéticos fixos no CI. O workflow de API roda mypy do motor, não de toda a API. Restauração inicial não deve depender apenas do pipeline da Etapa 3. F02/F09/F11/F14. |

Os 21 links Markdown locais dos contextos apontam para arquivos existentes.
Isso comprova o roteamento dos documentos, não a correção de suas afirmações.

## Achados que afetam o desenvolvimento

### F01 — Ingestão continua pendente nos documentos e no código

O [plano, bloco de identidade/ingestão](IMPLEMENTATION_PLAN.md#L21) exige
originais preservados, fontes reais, versões, importação e reconciliação.
[API CONTEXT](../apps/api/CONTEXT.md#L67) e
[web CONTEXT](../apps/web/CONTEXT.md#L66) mantêm ingestão e upload como próximos
trabalhos da Etapa 1. O OpenAPI gerado do código mantém 14 caminhos/19 operações;
`/sources`, `/imports`, `/snapshots`, `/quality`, `/lineage` e `/jobs`, sob
`/api/v1`, não existem.

| Parte do requisito | Prova no estado atual |
| --- | --- |
| Identidade | Emissor/instrumento/listagem existem como tabelas; faltam resolução de emissor, identificadores oficiais, vigências usadas e histórico de símbolos. |
| Fonte/tempo/revisões/snapshots | Preços manuais com fonte/data/hash e checksum da consulta. Sem envelope completo, cutoff de disponibilidade ou recuperação de snapshot por versão. |
| Fontes reais e cobertura | Nenhum adaptador financeiro implementado. Os contextos não acrescentaram integrações. |
| CSV/XLSX, mapeamento, prévia, reconciliação e originais | Ausentes. Exportação CSV não cobre esse fluxo. |
| Reimportação sequencial/concorrente/entre arquivos | Idempotência JSON com chave/identificador externo existe; não há parser de arquivos nem decisões de conciliação entre extratos. |
| Unidades/períodos/nulos/quarentena | Nulos e idade de avaliação manual têm tratamento parcial; normalização de escala/períodos e quarentena não existem. |
| Correção rastreável | Trilha de ações existe; retificação/estorno com versões e impacto ainda não. |

O detalhamento de código e testes está na [auditoria funcional anterior](STAGE_1_AUDIT.md).
A comparação de contextos confirma a lacuna, em vez de revelar uma rota oculta.

### F02 — Roteiros locais deixam critérios iniciais em etapas posteriores

O plano exige **linha de base efetivamente medida na Etapa 1**, em sua
[integração e portão](IMPLEMENTATION_PLAN.md#L25). A medição aparece apenas
na Etapa 2 em [scripts](../scripts/CONTEXT.md#L46),
[docs](CONTEXT.md#L43) e [engines](../packages/engines/CONTEXT.md#L75).
A Etapa 2 deve ampliar/comparar uma base já medida.

O plano também exige backup/restauração demonstráveis na
[Etapa 1](IMPLEMENTATION_PLAN.md#L24). A raiz e scripts reconhecem essa entrega,
mas o roteiro de [tests](../tests/CONTEXT.md#L50) só menciona restauração na
Etapa 3. Acrescentar o teste inicial de recuperação da cobertura entregue;
a Etapa 3 amplia o conjunto completo de dados/artefatos e operação.

[apps/CONTEXT](../apps/CONTEXT.md#L30) associa o processo worker à Etapa 3.
Não é obrigatório criar agora a pasta `apps/worker`, mas jobs aceitos em
segundo plano na Etapa 1 precisam de execução durável, retomada e estados
persistidos. Não interpretar o texto como licença para postergar essa garantia.

### F03 — Os roteiros de backend/motores não cobrem todas as sete skills

O [plano](IMPLEMENTATION_PLAN.md#L23) inclui mercado/watchlists, fundamentos,
macro, aprendizado e diário/teses/comentários básicos. A web lista páginas
pendentes, mas os roteiros locais de API e motores concentram-se no ledger,
ingestão, relatórios e módulos futuros. Faltam entregas locais explícitas para
S02/S03/S07/S23 e parte de S01/S12/S21, incluindo metas e performance.

Uma lista resumida não elimina esses requisitos. Completar os contratos e
responsáveis por serviço/motor, preservando as sete skills da Etapa 1. Não
substituir o portão por “bases funcionais” sem procedimentos, ferramentas,
avaliações, fontes e jornadas correspondentes.

### F04 — Autorização e campos de autoria/titularidade estão superdescritos

[API CONTEXT, linha 62](../apps/api/CONTEXT.md#L62) afirma que `member` só
insere operações em carteiras associadas a seus titulares autorizados.
O [require_writer](../apps/api/src/hub_api/security.py#L82) verifica o papel;
[POST /transactions](../apps/api/src/hub_api/main.py#L488) consulta a carteira,
sem consultar associação usuário–titular. Não há essa tabela/ACL nos modelos.

A política atual oferece acesso compartilhado ao grupo e escrita por papel.
O próprio prompt separa **usuário de acesso** de **titular econômico**. Não
inferir uma restrição individual que o produto não implementou, nem classificar
automaticamente compartilhamento autorizado como vazamento. Documentar a
política atual; se forem desejadas restrições adicionais, defini-las explicitamente.

A [raiz, linha 33](../CONTEXT.md#L33) generaliza `owner_id` e `created_by`
para todos os cadastros. [Models](../apps/api/src/hub_api/models.py#L61) mostra,
por exemplo, `Owner` com ID/nome e `Instrument` sem esses dois campos. Em
vários cadastros a autoria está no `AuditEvent`, não na linha da entidade.

### F05 — O contrato descrito para o motor não é seu contrato atual

[Engine CONTEXT](../packages/engines/CONTEXT.md#L42) descreve `PortfolioState`,
snapshots imutáveis, funções puras e exceções `InsufficientCashError` e
`InsufficientPositionError`. O código expõe `LedgerState`, `LedgerError` e
`apply_event(state, event) -> list[Posting]`; uma operação válida modifica
o estado em memória depois das validações. A imutabilidade do histórico
persistido é garantida em outra camada, pelas migrações.

Verificação em memória: depósito sintético levou `state.cash` de 0 para 100;
retorno do tipo `list`; `LedgerState.frozen == False`. Os nomes propostos não
existem no módulo. `EventType` contém `deposit`, `buy` etc. em minúsculas,
não as strings maiúsculas do contexto. Não usar os exemplos como API implementada.

Também não é verdadeira como descrição atual a afirmação de
[apps](../apps/CONTEXT.md#L4)/[API](../apps/api/CONTEXT.md#L46) de que nenhum
cálculo ocorre em serviços da API: [portfolio_service](../apps/api/src/hub_api/portfolio_service.py#L153)
calcula valor de mercado, custo médio, resultado não realizado e agregações.
Isso deve constar na fronteira observada e no contrato de reutilização,
sem criar fórmulas paralelas ou refatoração não justificada.

### F06 — Tecnologias, rotas e comandos de frontend divergem

[Web CONTEXT](../apps/web/CONTEXT.md#L4) cita Next.js 15/Tailwind; as
[dependências](../apps/web/package.json#L13) são Next.js **16.4.5**, React
19.3.1 e CSS próprio. Não há Tailwind nem Vitest. O comando de testes usa
`tsx --test tests/*.test.ts`; **25 testes passaram**, contra os 24 descritos.

P04 aparece como `/acoes` no contexto, enquanto a matriz propõe
[`/empresas/:instrument_id`](REQUIREMENTS_MATRIX.md#L57). Nenhuma das duas
rotas foi implementada. A matriz permite equivalentes, mas não há decisão
registrada que alinhe essa substituição; não tratar `/acoes` como rota existente.

A verificação visual local cita 1920/375 px. Essas larguras podem complementar,
mas não substituir 1440/1024/768/390 px exigidos no prompt. Aprovação das imagens
de referência não equivale a homologação visual das telas construídas.

### F07 — O inventário de componentes atribui capacidades inexistentes

Em [Web CONTEXT](../apps/web/CONTEXT.md#L15), Administração recebe titulares,
ativos e auditoria. Na implementação, membros ficam em Administração; titulares
em Carteiras; ativos em Operações; trilha de ações em Dados. Não há indicador
de saúde no `hub-shell` ou na página Administração.

`positions-table` renderiza a lista completa, sem paginação.
`use-resource` faz requisição por mudança de chave com cancelamento/estado;
não implementa polling periódico nem cache de consultas reutilizável.
`formatCurrency`/`formatPercent` não existem; os nomes reais incluem `money`,
`unitPrice`, `number` e `percent`. Esses contratos precisam refletir os arquivos
[positions-table](../apps/web/src/components/positions-table.tsx#L8),
[use-resource](../apps/web/src/lib/use-resource.ts#L9) e
[format](../apps/web/src/lib/format.ts#L10).

### F08 — O contexto operacional descreve outro formato de runtime

[Scripts CONTEXT](../scripts/CONTEXT.md#L11) chama o sincronizador de
bidirecional. Ele copia `.agents` para `.claude` e atualiza o lock, sem
propagar edições do espelho de volta. Essa distinção protege a fonte canônica.

`scripts/windows/runtime.py` é um ponto de entrada que importa
`hub_api.windows_runtime.main`. Downloads/extração estão no PowerShell;
supervisão/cluster ficam no módulo da API. O
[manifesto real](../scripts/windows/downloads.json) usa `schema_version`,
`python_version` e `downloads` com `uv`, `node`, `postgres`, `vclibs`.
Não há Caddy nem objeto `python` com URL/hash como no contrato ilustrado.

### F09 — A verificação de integridade das skills falha

Executado sem sincronizar ou alterar arquivos:

```text
python scripts/sync_agent_skills.py --check
exit 1
skills-lock.json desatualizado
```

Os espelhos examinados correspondem às origens, mas `computedHash` diverge
em cinco entradas: `constraint-driven-development`, `idea-refine`,
`performance-optimization`, `reverse-engineer-anything`, `security-and-hardening`.
Não há afirmação de adulteração: o resultado é inconsistência entre conteúdo
e lockfile. Revisar a origem dos bytes antes de regenerar o lock.

Existem 26 skills **de engenharia**, não 26 funcionalidades financeiras.
O check de sincronização ainda não aparece nos workflows. O roteiro de
`.agents`/`.github` reconhece essa pendência corretamente, mas a instrução
de que o comando deve passar ainda não se verifica nesse commit.

### F10 — Testes e casos normativos estão descritos incorretamente

[tests/CONTEXT](../tests/CONTEXT.md#L11) e engines atribuem Hypothesis ao
arquivo adversarial. Na árvore atual, o teste com `@given` está em
`tests/unit/test_ledger.py`; o arquivo adversarial contém casos determinísticos
e parametrizados. A fixture de integração cria um banco temporário em um
PostgreSQL disponível e usa `fastapi.testclient.TestClient`, não testcontainers
ou `httpx.AsyncClient`.

As referências T15/T21/T25 do roteiro não preservam seus significados:

| Caso | Significado do prompt |
| --- | --- |
| T15 | Split/grupamento sem aporte preserva patrimônio; emissão com aporte tem efeitos próprios. |
| T21 | Não contar provento duas vezes em preço ajustado e caixa. |
| T25 | Distinguir provento anunciado, cancelado e recebido. |
| T26 | Performance em moeda-base com câmbio e datas coerentes. |

Não reduzir os critérios da Etapa 1 a essa lista: T04/T05, T08–T12, T32,
T36 e T45 cobrem partes essenciais de importação, qualidade, disponibilidade,
retomada, restauração e correção. O [plano](IMPLEMENTATION_PLAN.md#L21)
continua exigindo esses resultados; nomes de testes e contagens não os substituem.

### F11 — O comando mypy do contexto não é o gate aprovado pelo CI

Executados no ambiente Python já instalado:

```text
.venv/bin/mypy apps/api/src
exit 1 — Found 136 errors in 7 files (checked 11 source files)

.venv/bin/mypy
exit 0 — Success: no issues found in 2 source files
```

A [configuração](../pyproject.toml#L38) seleciona `hub_finance` para o comando
sem caminhos, usado pelo CI. [API CONTEXT](../apps/api/CONTEXT.md#L93) indica
outro escopo. São erros de checagem estática, não 136 falhas de execução da API.
Documentar a cobertura real e tratar a tipagem adicional como trabalho pendente,
sem apresentar o CI do motor como aprovação de toda a API.

### F12 — Política numérica e fiscal foi simplificada indevidamente

[packages](../packages/CONTEXT.md#L13) e
[tests](../tests/CONTEXT.md#L49) exigem equivalência bit a bit de qualquer
acelerador. O prompt §5.5 manda respeitar tolerâncias e o ambiente validado,
sem exigir identidade binária fora da política. Dinheiro canônico usa
Decimal/NUMERIC; matrizes e derivadas científicas podem usar float64 com
tolerâncias justificadas. O plano não exige um backend novo nem igualdade
universal de resultados estocásticos entre runtimes distintos.

O roteiro de [engines](../packages/engines/CONTEXT.md#L74) cita um limite de
isenção fiscal como regra pronta. O [plano da Etapa 2](IMPLEMENTATION_PLAN.md#L36)
e a S16 exigem fonte oficial, categoria, titular e vigência verificados antes
de implementar. Esta auditoria não valida uma regra fiscal atual.

### F13 — Nomes públicos e instalação precisam corresponder ao código

O modelo é `AuditEvent`, não `AuditLog`. A CLI oferece `create-admin` e
`setup-admin`, não `bootstrap-admin` (`python -m hub_api.cli --help` conferido).
Não existe `pyproject.toml` ou `setup.py` em `packages/engines`; o manifesto
da raiz empacota `hub_api` e `hub_finance`, e o bootstrap usa `uv sync --locked`.
O comando de instalação descrito em [packages](../packages/CONTEXT.md#L20)
não corresponde ao projeto empacotado. Não foi executada instalação com esse
comando incorreto.

### F14 — Workflow existente não comprova todas as garantias narradas

[verify.yml](../.github/workflows/verify.yml#L2) e `windows.yml` disparam em
`push`/`pull_request` sem filtros de branch. Não estão restritos a
`main`/`codex/*` como diz `.github/CONTEXT.md`. O CI utiliza também credenciais
sintéticas fixas; isso difere de gerar todas em memória, sem implicar exposição
de credenciais pessoais. Não reproduzir valores sensíveis ao corrigir o texto.

Existência do workflow não comprova proteção obrigatória de branch. Regras
remotas de proteção não foram auditadas nesta tarefa. Checks de links, lock
e recuperação ainda precisam de integração conforme a cobertura do plano.

## Verificações executadas nesta comparação

| Verificação | Resultado |
| --- | --- |
| Atualização do Git e inventário de contextos | 11 CONTEXT.md lidos; base `main` em `c509cdd`; contextos equivalentes aos de `d6e8a68`. |
| Diferenças de produto desde a auditoria anterior | Nenhuma mudança em código de apps, engines ou testes; apenas contextos nessas pastas. |
| Links Markdown locais nos 11 contextos | 21 válidos, zero quebrados. |
| OpenAPI importado sem conexão ao banco | 14 caminhos/19 operações; ingestão/jobs continuam ausentes. |
| Contrato do motor em memória e CLI `--help` | Estado mutável/retorno de lançamentos e comandos reais confirmados. |
| `python scripts/sync_agent_skills.py --check` | Falhou: lockfile divergente em cinco hashes. |
| `.venv/bin/mypy apps/api/src` | Falhou: 136 erros em sete arquivos. |
| `.venv/bin/mypy` | Passou: motor, dois arquivos. |
| `npm --prefix apps/web test` | 25 testes passaram; runner `tsx`/Node. |

Não foram repetidos testes de integração PostgreSQL, build, instalação Windows,
QA visual ou benchmarks. Não houve alteração de código financeiro, migrações,
contas, documentos originais ou dados do usuário. O check de lock foi somente
de leitura; a falha permanece registrada para correção posterior.

## Escopo proposto para continuar após autorização

1. Alinhar os 11 contextos aos contratos reais e ao plano: nomes, tecnologias,
   comandos, critérios de teste, papéis e responsáveis por requisitos da Etapa 1.
   Revisar a divergência do lock, corrigir com rastreabilidade e integrar checks
   pertinentes. Não trocar frameworks ou regras financeiras para satisfazer
   uma descrição documental incorreta.
2. Entregar identidade/proveniência/snapshots/originais, correções versionadas
   e reconciliação; preparar jobs duráveis antes de aceitar imports em segundo plano.
3. Implementar CSV/XLSX com mapeamento, prévia, confirmação, deduplicação
   sequencial/concorrente/entre arquivos e rastreabilidade; integrar fontes reais
   com cobertura demonstrada e qualidade/quarentena.
4. Completar as sete skills/páginas da Etapa 1, performance e relatórios,
   wrappers/MCP, recuperação inicial, medições e jornadas previstas.

Essa ordem mantém as três etapas e seus portões. O pedido atual autoriza
comparar e relatar; a execução desse escopo depende da próxima autorização
do usuário. Nenhum item foi promovido a concluído por este relatório.
