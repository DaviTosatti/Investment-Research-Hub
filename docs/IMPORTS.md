# Importação guiada de operações — Etapa 1

Em **Dados e auditoria → Importações**, selecione a carteira e a fonte do extrato,
envie o arquivo e confira o mapeamento das colunas. O envio e a prévia não lançam
operações. A gravação ocorre somente em **Confirmar importação**, depois da
conferência. O grupo pode consultar os arquivos; administradores e membros podem
importar. O titular é o da carteira selecionada e a autoria é a conta autenticada.

## Formatos e cobertura entregue

- CSV UTF-8 (com ou sem BOM) ou Windows-1252, com separador selecionado: ponto e
  vírgula, vírgula ou tabulação. XLSX sem macros; informe a aba quando houver várias.
- Até **2 MiB, 500 linhas de dados e 40 colunas** por arquivo. XLSX descompactado
  limitado a 16 MiB/400 partes. Processamento síncrono limitado, sem job em segundo
  plano. Arquivos fora dos limites são recusados, nunca truncados silenciosamente.
- BRL, valores monetários em reais, quantidades em unidades e desdobramento como
  fator. Não há inferência de milhares/milhões, moeda estrangeira ou câmbio.
- Tipos: `deposit`/aporte, `withdrawal`/retirada, `buy`/compra, `sell`/venda,
  `dividend`/dividendo, `fee`/taxa, `tax`/imposto, `split`/desdobramento.
- Datas de negociação/liquidação; data futura, ativo desconhecido, falta de caixa,
  venda além da posição, moeda incompatível e bruto divergente ficam em quarentena. Bruto mapeado explicitamente como zero
  não autoriza substituição pelo valor calculado; retire o mapeamento para derivar
  o bruto de compra/venda. A prévia expõe também `calculated_gross_amount`.
  A ordem é data e, dentro do dia, ordem no arquivo. Novos eventos precisam ser
  posteriores ou iguais ao último dia do histórico; não é conciliação intradiária.
- Campos opcionais **não mapeados**: taxas/tributos/quantidade/preço/bruto usam zero
  quando não exigidos pelo tipo; liquidação usa negociação; moeda usa BRL. Uma
  célula monetária **mapeada e vazia** continua nula e bloqueia a linha. Não vira zero.
- Números XML do XLSX são lidos diretamente como texto decimal, sem float. Texto
  no XLSX e valores CSV seguem o separador decimal escolhido, sem agrupamento de
  milhares. Datas Excel são convertidas em datas ISO; fórmulas, erros e formatos
  percentuais incompatíveis ficam em quarentena. Fórmulas nunca são executadas.

## Conferência e reconciliação

Cada linha recebe um estado: pronta, duplicada, precisa de revisão, quarentena
ou excluída explicitamente. A prévia mostra valores normalizados, mensagens,
possíveis correspondências e o caixa calculado pelo mesmo motor das operações
manuais. Enquanto houver linhas pendentes, a confirmação é bloqueada. O caixa
da prévia representa somente as linhas prontas; não é o resultado de linhas
que ainda precisam ser corrigidas ou decididas.

Use uma **fonte estável** para os extratos da mesma origem. A referência externa
identifica a execução naquela fonte e carteira. Mesma referência com os mesmos
dados econômicos reutiliza a operação; com valores diferentes exige revisão.
Referências diferentes na mesma fonte permitem operações iguais legítimas.
Referências numéricas do XLSX são normalizadas como inteiros exatos (por exemplo,
`1E+2` e `100`); referências textuais preservam sua identidade, inclusive zeros
à esquerda. Identificações numéricas fracionárias exigem revisão.
Sem identidade externa suficiente, a comparação ignora liquidação e encargos
opcionais, pois sua ausência não comprova uma operação distinta. Uma possível
igualdade econômica produz uma sugestão de duplicata: escolha excluir ou justifique que se trata de uma operação distinta.
Uma referência nova em outra fonte não elimina essa conferência. A prévia
informa o total de candidatos e no máximo 20 referências por linha.

Reenviar os mesmos bytes para a mesma carteira/fonte/configuração reutiliza a
importação. Arquivos diferentes são comparados ao histórico e às linhas do
próprio arquivo. A confirmação mantém lock por carteira, recibo único e operações
na mesma transação PostgreSQL. Se o histórico mudar desde a prévia, o servidor
recusa com `STALE_PREVIEW`: gere outra prévia e confira novamente. Repetir a
confirmação já concluída retorna o mesmo recibo, sem novos lançamentos.

## Originais, revisões e auditoria

O arquivo original é preservado byte a byte no PostgreSQL, com SHA-256, tamanho,
fonte, carteira, titular, autor e horário de envio. Não fica no Git nem em diretório
público. O download exige sessão. A identidade do ativo é o ID cadastrado; o par
ticker/mercado precisa resolver uma listagem existente. Não são criados ativos por
aproximação de nome ou ticker.

Alterar o mapeamento, corrigir um campo ou decidir sobre uma linha gera **nova
prévia imutável**, com motivo da correção/decisão e autoria. As revisões anteriores
e as células originais continuam consultáveis. Depois da confirmação, o recibo
liga linha → operação → prévia → arquivo/fonte. Prévia antiga não substitui a
revisão mais recente; importação confirmada não é editável.

Essas correções são **anteriores ao lançamento**. Retificação/estorno de operações
já confirmadas continua pendente na Etapa 1. Não é correto corrigir uma operação
já lançada trocando a referência externa para forçar outra inserção.

## Contrato HTTP disponível após login

| Método e rota em `/api/v1` | Uso |
| --- | --- |
| `GET/POST /sources` | Fontes de arquivos fornecidos pelo usuário |
| `GET /imports` | Histórico paginado, filtro `portfolio_id` |
| `POST /imports` | Bytes do arquivo; query `portfolio_id`, `source_id`, `filename`, `delimiter`, `encoding`, `sheet` opcional |
| `GET /imports/{id}` | Cabeçalhos, amostra, última prévia e recibo |
| `GET /imports/{id}/original` | Download autenticado do original, com hash no cabeçalho |
| `POST /imports/{id}/preview` | Mapeamento, formatos, correções e decisões; cria uma revisão |
| `POST /imports/{id}/confirm` | `{preview_id}`; gravação atômica do lote aprovado |
| `GET /snapshots?import_id={id}` | Lista paginada de revisões da importação |
| `GET /snapshots/{id}` | Prévia congelada e seus dados/regras |
| `GET /quality` | Qualidade por importação, com paginação e filtro de carteira |
| `GET /lineage?import_id={id}` | Fonte, titular, original, revisões e recibo de operações |

Uploads usam `application/octet-stream`; demais escritas usam JSON e todas
incluem `X-Hub-Request: 1`. Schemas completos em `GET /api/v1/openapi.json`.
`mapping` associa campo canônico a cabeçalho; `decimal_separator` é `.` ou `,`;
`date_format` é `YYYY-MM-DD` ou `DD/MM/YYYY`. `event_values` permite mapear rótulos
da origem para tipos canônicos. `edits` contém `row_number`, `values`, `reason`;
`decisions` contém `row_number`, `action` (`skip` ou `create`), `reason`.

## Limites de conclusão

`/sources` aqui registra a origem dos arquivos; não é conector de cotações,
CVM, BCB ou outra fonte externa. `/snapshots` contém prévias de importação; o
checksum do dashboard continua sem snapshot de análise persistido. `/quality`
avalia a importação e não certifica demonstrações contábeis ou cobertura de
provedores. Jobs duráveis, fornecedores externos, identidade oficial/histórica,
retificação de eventos lançados e demais requisitos da Etapa 1 permanecem no plano.

English: authenticated CSV/XLSX statement imports now preserve originals, version
mapping previews, quarantine invalid rows, reconcile duplicates and atomically
post approved rows through the canonical ledger. This is a bounded synchronous
workflow. External providers, durable jobs, posted-event corrections and the
remaining Stage 1 gates are still pending.
