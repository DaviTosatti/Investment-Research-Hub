# Investment Research Hub — contexto e normas para colaboradores

Atualizado em **12/11/2026**, horário de São Paulo. Destinado aos colegas
autorizados por Davi e aos assistentes de IA que os apoiarem. Pode ser enviado
como um único Markdown; os arquivos citados complementam o contexto quando a
pasta do projeto também estiver disponível.

## 1. Identificação e ponto de partida

- Projeto: **Investment Research Hub**, plataforma privada de pesquisa,
  aprendizado e acompanhamento contábil-financeiro de investimentos.
- Repositório: [DaviTosatti/Investment-Research-Hub](https://github.com/DaviTosatti/Investment-Research-Hub).
- Responsável pela integração e aprovação final de PRs: **Davi (`DaviTosatti`)**.
- Fotografia de documentação/código recebida: commit `e54b6d5`; último código
  funcional validado neste chat: `02eaddb698fc1e6320f603b702d895be2762b31c`.
- Branch desse trabalho: `codex/auditoria-contextos-etapa-1`.
  [PR #3](https://github.com/DaviTosatti/Investment-Research-Hub/pull/3): aberto,
  em rascunho e ainda sem merge na consulta desta atualização.
- A `main` consultada estava em `c509cdd`, anterior à nova ingestão. Portanto,
  uma pasta da `main` pode não conter o importador descrito aqui. Conferir a
  branch e os SHAs antes de diagnosticar uma funcionalidade como ausente.

Esta é uma fotografia de repasse, não um registro atualizado automaticamente.
Ao retomar, confira o Git, o código e o `docs/STATUS.md` mais recente. Receber
este documento não atribui uma tarefa de desenvolvimento ao assistente: o colega
informa qual incremento quer executar. Compartilhar a pasta ou o repositório
também não compartilha sessões do Codex nem um banco de dados em execução.

## 2. O que foi decidido neste chat

1. Implementar o produto descrito em `docs/reference/Promptx.txt`, preservando
   **exatamente três etapas** e todo o planejamento das 23 skills de negócio.
2. Usar as **11 referências visuais aprovadas**: identidade fintech escura,
   FinSight/Stockly para o dashboard e Chainx para a sidebar. O detalhamento está
   em `docs/VISUAL_REFERENCES.md`; o padrão pessoal de dashboards de adquirência
   não se aplica ao Hub.
3. Registrar progresso verificável e publicar incrementos coerentes no GitHub
   com Conventional Commits, sem confundir um commit com uma etapa de produção.
4. Entregar **execução Windows nativa**. A prévia remota do Codex havia falhado;
   ela não era prova de falha da aplicação. O usuário não dispõe de Linux/WSL.
5. Corrigir mensagens e entrada do primeiro cadastro/login, exibindo o erro de
   validação sem expor dados sensíveis. A senha mantém mínimo de 12 caracteres.
   Nenhuma conta pessoal do usuário foi criada como parte do desenvolvimento.
6. Auditar a Etapa 1, especialmente identidade, ingestão e qualidade. Depois,
   comparar os contextos de cada pasta com o plano, antes da retomada autorizada.
7. Preservar em **cada `CONTEXT.md` tanto o inventário real quanto o roteiro
   das Etapas 1, 2 e 3**. Corrigir um inventário não autoriza apagar compromissos
   futuros. As auditorias antigas continuam identificadas como históricas.
8. Continuar a Etapa 1. A entrega mais recente implementou ingestão CSV/XLSX
   integrada, auditável e verificada em Linux e Windows. **A etapa continua parcial.**
9. Permitir colaboração dos colegas por contas próprias, branches e PRs. O link
   de compartilhamento deste chat é uma cópia estática de leitura, não uma sessão
   conjunta de desenvolvimento.

## 3. As três etapas que precisam ser preservadas

| Etapa | Cobertura planejada | Skills de negócio | Estado nesta fotografia |
| --- | --- | --- | --- |
| 1 | Fundação, experiência visual, dados e acompanhamento; 12 páginas-base | S01, S02, S12, S03, S07, S21, S23 — **7** | Em implementação; nenhum módulo/skill integral declarado concluído |
| 2 | Análise avançada, classes de ativos e estratégias | S19, S10, S09, S15, S04, S16, S05, S17, S06, S14, S08, S11 — **12** | Não iniciada |
| 3 | Comitê IA, colaboração ampliada, monitoramento e operação completa | S13, S18, S20, S22 — **4** | Não iniciada |

Fonte de escopo: `docs/IMPLEMENTATION_PLAN.md` e
`docs/REQUIREMENTS_MATRIX.md`, derivados do Promptx original. Existem 23 páginas
previstas no produto completo; isso não significa 23 páginas prontas. As
**26 skills de desenvolvimento** em `.agents/skills/` são ferramentas de
engenharia, distintas das **23 skills financeiras** S01–S23. O ZIP das duas
skills originais S01/S02 mencionado no prompt não foi localizado; não alegar
que seu conteúdo foi importado ou revisado.

## 4. Arquitetura e regras financeiras

Monólito modular, com frontend e API em processos separados:

| Área | Implementação atual | Arquivos de entrada |
| --- | --- | --- |
| Interface | Next.js 16.4.5, React 19.3.1, TypeScript, CSS próprio, PT/EN | `apps/web/package.json`, `apps/web/CONTEXT.md` |
| API/persistência | Python 3.12 no CI, FastAPI, Pydantic, SQLAlchemy, Alembic, PostgreSQL 17.6 | `pyproject.toml`, `apps/api/CONTEXT.md` |
| Cálculo canônico | `hub_finance`, motor `average-cost-brl/1.0.1` | `packages/engines/CONTEXT.md`, `docs/MODEL_REGISTRY.md` |
| Ingestão | Parser CSV/XLSX, serviço de importação e gravação transacional compartilhada | `apps/api/src/hub_api/import_service.py`, `apps/api/src/hub_api/transaction_service.py` |
| Operação Windows | PowerShell 5.1 e runtimes portáteis com hashes fixados | `scripts/windows/Start-Hub.ps1`, `docs/WINDOWS.md` |

Invariantes para qualquer alteração:

- Dinheiro usa `Decimal`/`NUMERIC`; valores financeiros transitam como strings
  JSON. Não introduzir `float` no ledger nem fórmulas financeiras paralelas no
  frontend. Reutilizar os motores canônicos na API e nas futuras interfaces.
- Titular econômico é diferente de usuário de acesso e de autor da alteração.
  Preservar essa distinção, a conta, a carteira e a trilha de autoria.
- Ledger e histórico são imutáveis/balanceados. Idempotência e lock por carteira
  protegem a gravação; uma nova referência externa não é uma correção de lançamento.
- São registrados fatos econômicos já realizados. O Hub não envia ordens,
  pagamentos nem operações para corretoras.
- O grupo compartilha consultas; a escrita depende de `admin`/`member`.
  `viewer` é somente leitura. Não presumir isolamento por usuário/titular que
  o modelo atual não implementa.
- Sem cotação, valor de mercado fica indisponível; não fabricar preços ou
  substituir silenciosamente mercado por custo. Moeda/unidade/data devem ser claras.
- Rust/Julia só entram com benefício e equivalência medidos. Não criar pastas,
  serviços ou mocks para aparentar a conclusão de módulos futuros.

## 5. O que já funciona no recorte entregue

### Fundação e acompanhamento

- Login por sessão privada e papéis `admin`, `member`, `viewer`; administração
  de membros; titulares, contas, carteiras e cadastro básico de ativos/listagens.
- Eventos `deposit`, `withdrawal`, `buy`, `sell`, `dividend`, `fee`, `tax`, `split`.
  Custo médio, caixa, posições, resultado realizado e consultas canônicas;
  preços manuais persistidos, mercado quando disponível e exportação CSV.
- Páginas integradas `/inicio`, `/carteiras`, `/operacoes`, `/dados` e
  `/administracao`, com a cobertura parcial descrita nos contratos.
- Execução Windows pelos três atalhos CMD e persistência ao reiniciar.

### Ingestão, qualidade e auditoria

Em **Dados e auditoria → Importar operações** (`/dados#importacoes`):

1. Selecionar carteira/titular e fonte; enviar CSV ou XLSX.
2. Conferir amostra, mapear colunas e indicar formatos de número/data.
3. Gerar prévia, conferir efeitos e tratar linhas prontas, duplicadas,
   ambíguas, em quarentena ou explicitamente excluídas.
4. Corrigir campos ou justificar decisões, produzindo nova prévia imutável.
5. Confirmar somente a revisão atual sem pendências. Gravar operações e recibo
   atomicamente pelo mesmo caminho contábil das operações manuais.
6. Consultar revisões, baixar o original e rastrear linha → operação → prévia
   → arquivo/fonte. Repetir uma confirmação concluída reutiliza o recibo.

O original permanece byte a byte no PostgreSQL com hash e metadados. São
tratados reenvio sequencial, confirmação concorrente, sobreposição entre
arquivos/fontes, nulos, ambiguidades e prévia que ficou desatualizada.
XLSX é lido sem converter dinheiro para float e sem executar fórmulas.

Rotas relativas a `/api/v1`:

| Método/rota | Cobertura |
| --- | --- |
| `GET/POST /sources` | Fontes de extratos enviados pelo grupo |
| `GET/POST /imports`, `GET /imports/{id}` | Upload privado e consulta de importações |
| `GET /imports/{id}/original` | Download autenticado do original |
| `POST /imports/{id}/preview` | Mapeamento, correções, decisões e nova revisão |
| `POST /imports/{id}/confirm` | Confirmação atômica da revisão aprovada |
| `GET /snapshots`, `GET /snapshots/{id}` | Prévias persistidas da importação |
| `GET /quality`, `GET /lineage` | Qualidade e rastreabilidade do recorte de ingestão |

Inventário da API nesta base: **24 caminhos / 31 operações HTTP**.
O contrato exato, parâmetros, permissões e limites estão em `docs/IMPORTS.md`,
`docs/API_CONTRACT.md` e no OpenAPI autenticado `/api/v1/openapi.json`.
Swagger `/docs` está desativado.

## 6. Limites e pendências reais da Etapa 1

- Ingestão atual: **BRL, 2 MiB, 500 linhas de dados, 40 colunas**, síncrona.
  Não há worker/job durável entregue. Arquivos excessivos são recusados.
- `/sources` representa extratos enviados pelo grupo; não comprova integração
  com provedor de mercado, CVM, Banco Central ou outra fonte externa.
- `/snapshots` preserva prévias de importação; não representa ainda todo o
  contrato de snapshots de análises/fundamentos e disponibilidade histórica.
- Correções entregues acontecem **antes da confirmação**. Estorno/retificação
  versionada de eventos já lançados ainda está pendente.
- Identidade oficial/histórica de emissor, instrumento e múltiplas listagens
  precisa ser completada. Cadastro básico e resolução por ID não encerram o bloco.
- Eventos são cronológicos; não há suporte completo a transferências, câmbio,
  demais eventos corporativos, performance TWR/MWR ou tributação abrangente.
- Mercado/watchlists, fundamentos, macro, Mentor, diário/teses, relatórios nos
  formatos planejados e wrappers/MCP precisam completar a cobertura da etapa.
- Faltam jobs duráveis, restauração comprovada em destino vazio, benchmark
  representativo, jornadas/avaliações das sete skills e os demais portões do plano.
- Mypy no CI cobre **o motor `hub_finance`**, não toda a API. Existência de CI
  não comprova proteção obrigatória de branch nem aprovação funcional de uma etapa.

Prioridade sugerida no handoff: retificação/estorno rastreável, depois ampliar
ingestão/identidade/fontes e completar os demais blocos conforme dependências.
A distribuição de tarefas entre colegas deve declarar arquivos e contratos
sob responsabilidade de cada um, com Davi responsável pela integração.

## 7. Como iniciar e quais evidências já existem

**Windows 10/11 x64:** extrair a pasta completa e executar `Iniciar Hub.cmd`.
O iniciador prepara dependências e abre `http://127.0.0.1:8766`. Usar
`Parar Hub.cmd` para encerrar e `Verificar Hub.cmd` para diagnóstico da instalação.
O primeiro administrador é solicitado localmente, quando ainda não existe.
Cada colega usa suas próprias credenciais.

Runtimes, configuração e banco ficam em
`%LOCALAPPDATA%\InvestmentResearchHub`, separados do código. API `8765`,
interface `8766` e PostgreSQL `54329` escutam somente em `127.0.0.1`.
Cada instalação local tem seus próprios dados; compartilhar a pasta não cria
um servidor comum para o grupo. O guia operacional é `docs/WINDOWS.md`.

Evidência histórica no código `02eaddb`:

- **318 testes Python e 40 web**, lint, tipagem configurada, migrações, build
  e integridade das 26 skills aprovados em
  [Linux](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482596)
  e [Windows](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482586).
- Windows Server 2022 x64/PowerShell 5.1: instalação limpa com espaços/acentos,
  login, ledger Decimal, importação pelo frontend, original/recibo e idempotência
  após reinício, recusa de segunda instância e atalhos CMD.
- Chromium sobre build de produção: importação, correção, confirmação, download,
  recarga, histórico e viewer; larguras 1440/1024/768/390, sem erro JS observado.
- [ZIP Windows desse código](https://github.com/DaviTosatti/Investment-Research-Hub/actions/runs/42911482586/artifacts/13808241171),
  com retenção informada até 10/12/2026. Após expirar, consultar os runs aprovados.

Esses resultados não validam automaticamente commits novos. Não houve controle
ou homologação do computador do usuário. `Verificar Hub.cmd` também não substitui
as suítes de desenvolvimento/CI. O registro detalhado é `docs/STATUS.md`.

## 8. Como o GPT do colega deve ler o projeto

1. Identificar branch/SHA e verificar trabalho local com `git status`.
2. Ler `AGENTS.md`, este documento, `docs/STATUS.md` e `docs/HANDOFF.md`.
3. Conferir a tarefa no `docs/IMPLEMENTATION_PLAN.md` e na matriz de requisitos.
4. Usar `CONTEXT.md` da raiz para navegar e ler os contextos da área afetada.
   Distinguir inventário implementado, fotografia histórica e roteiro futuro.
5. Conferir código, contratos e testes antes de propor alteração. Em divergência,
   apontar a diferença e verificar evidência; não apagar o roteiro nem presumir
   que um documento antigo reflete a implementação nova.
6. Consultar `docs/VISUAL_REFERENCES.md` quando alterar UI e
   `docs/COMPUTE_ARCHITECTURE.md` quando alterar motores.
7. Aplicar as regras de contribuição abaixo e em `CONTRIBUTING.md`.

Nesta cópia não há `.codex/` versionado. As skills de engenharia canônicas ficam
em `.agents/skills/`; `.claude/` é espelho gerado. Se o colega receber `.codex/`
adicional, conferir seu conteúdo e origem: não presumir que substitui os
contratos do repositório. Alterações nas skills são feitas em `.agents/`, seguidas
de `python scripts/sync_agent_skills.py` e do check `--check`.

Ao compartilhar o projeto, enviar código e contexto autorizados; conferir uma
eventual `.codex/` local para excluir autenticação, tokens e histórico pessoal.
Não distribuir `.env`, `data/`, bancos, extratos, carteiras pessoais, backups,
sessões ou o diretório pessoal de configuração do Codex. O compartilhamento
autorizado entre colegas não transforma o projeto privado em código público.

## 9. Normas de branches, commits e pull requests

### Trabalho e publicação

1. **Uma tarefa coerente por branch e PR.** Sugestão de nome:
   `feat/etapa-1-<assunto>-<autor>`, `fix/<assunto>-<autor>` ou `docs/<assunto>-<autor>`.
   Trabalhos paralelos devem delimitar arquivos/contratos para evitar sobreposição.
2. A base padrão de integração é `main`. Se a tarefa depende do importador ainda
   no PR #3, partir da branch desse PR e declarar **"Depende de #3"**. Abrir PR
   dependente contra essa branch enquanto a dependência não for integrada; não
   enviar todo o trabalho do colega como se fosse uma nova entrega própria.
3. Preservar alterações locais de outras pessoas. Atualizar a base com merge
   quando necessário; não fazer force push, reset destrutivo ou reescrever
   commits publicados. Resolver conflitos revisando o resultado com os responsáveis.
4. Fazer commits por incremento validado e publicar na própria branch. Não fazer
   push direto na `main`, habilitar auto-merge nem executar merge pelo agente.
5. Títulos de PR e commits usam **Conventional Commits**, em português claro:
   `feat(ingestao): reconciliar extratos sobrepostos`,
   `fix(ledger): preservar custo em desdobramentos`,
   `docs(colaboracao): registrar contexto e regras de PR`.
   Tipos: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `chore`, `ci`.
   Preferir até 72 caracteres, sem ponto final. Incompatibilidade usa `!` e
   `BREAKING CHANGE:` com orientação de migração.
6. Atualizar STATUS com evidências e pendências; atualizar HANDOFF/contextos e
   contratos afetados. Manter os três roteiros em cada contexto. Não marcar
   uma skill ou etapa inteira como concluída por ter entregue um recorte.

### Conteúdo obrigatório do PR

- **Problema e comportamento entregue:** explicar o que o usuário consegue fazer
  depois da alteração; evitar apenas listar arquivos ou narrar a conversa com a IA.
- **Escopo:** etapa, requisito(s), dependências, módulos afetados e pendências.
- **Como conferir:** passos reproduzíveis, dados sintéticos e resultado esperado.
- **Evidências:** ambiente, comando, resultado, SHA testado e links de CI. Dizer
  claramente o que não foi executado e por quê; teste antigo não valida código novo.
- **Dados/compatibilidade:** migrações, efeito no histórico, formato de entrada/saída,
  configuração nova e procedimento de recuperação quando aplicável. Não prometer
  reversão de migração sem evidência.
- **UI, quando alterada:** capturas reais e conferência das larguras pertinentes,
  estados vazio/erro/carregando/parcial, teclado/foco e PT/EN. Não anexar dados reais.
- **Limites:** riscos concretos, cobertura ainda parcial e próximos requisitos.

Modelo que acompanha o projeto: `.github/pull_request_template.md`. Se o GitHub
não preencher o texto automaticamente, copiar o template manualmente.

### Verificação proporcional e solicitação de aprovação

- API/motor: Ruff, `uv run mypy` no escopo configurado, testes pertinentes e,
  quando houver mudança de banco, `alembic upgrade head`/`alembic check` em banco
  de desenvolvimento/teste. Integração usa banco isolado, nunca limpa dados pessoais.
- Web: testes, typecheck, lint e build; conferir a jornada quando afetada.
- Windows/runtime: verificar o fluxo nativo pelo workflow `Windows Native`;
  teste Linux não comprova compatibilidade com Windows.
- Skills: `python scripts/sync_agent_skills.py --check`.
- Documentação isolada: conferir fatos, links locais, coerência e
  `git diff --check`; não inventar uma nova execução das suítes financeiras.
- O pipeline completo é `scripts/check.sh`, com dependências/PostgreSQL preparados.
  Comandos efetivos e versões estão nos manifests e workflows; evitar copiar
  comandos antigos de um contexto sem conferir seu escopo.

Abrir **Draft PR** enquanto faltar validação ou houver pendência impeditiva.
Para solicitar aprovação, preencher o template, conferir o diff/segredos,
confirmar o SHA publicado, verificar os jobs `api`, `web` e `native` no commit
atual e solicitar revisão de **`DaviTosatti`** pela interface do PR. Se não houver
permissão para atribuir revisor, informar a Davi o link, SHA e limitações.

**Só Davi decide a integração final.** Nenhum colega ou GPT deve aprovar o
próprio trabalho, interpretar silêncio como aprovação ou executar merge sem
autorização explícita de Davi. Novas alterações após a revisão exigem nova
conferência e aprovação. Falhas/bloqueios concretos ficam registrados no PR.

Estas são normas de trabalho; este incremento não configura regras remotas de
proteção de branch, permissões do GitHub ou convites de colaboradores.

## 10. Mensagem pronta para iniciar o GPT do colega

```text
Leia docs/CONTEXTO_PARA_COLABORADORES.md e AGENTS.md neste projeto.
Confira a branch, o estado do Git, docs/STATUS.md, docs/HANDOFF.md e os
CONTEXT.md da área da tarefa. Preserve o plano de exatamente três etapas,
o inventário real e os roteiros futuros. Use o código e as evidências atuais
para conferir afirmações históricas. Antes de editar, resuma o que existe,
a lacuna da tarefa e os arquivos/contratos que pretende alterar.
Implemente apenas a tarefa que eu informar, com validação proporcional,
Conventional Commits, atualização de contexto e PR para revisão de DaviTosatti.
Não crie contas pessoais, não use dados reais em testes nem faça merge.

Minha tarefa é: [descrever o incremento e os critérios de aceite].
```
