# Contribuição e publicação incremental

Para retomar com colegas ou outro assistente, leia
[o contexto e as normas de colaboração](docs/CONTEXTO_PARA_COLABORADORES.md).
O aprovador final é **Davi (`DaviTosatti`)**. As normas abaixo aplicam-se também
a alterações feitas com auxílio de IA.

Cada commit representa uma mudança coerente, revisável e descrita pelo seu efeito.
O prefixo convencional para documentação é `docs`, conforme Conventional Commits.

| Tipo | Uso | Exemplo |
| --- | --- | --- |
| `feat` | Funcionalidade | `feat(ledger): registrar compras com custo de aquisição` |
| `fix` | Correção | `fix(ledger): preservar custo no desdobramento` |
| `docs` | Documentação | `docs(progress): registrar evidências da etapa 1` |
| `test` | Testes | `test(api): verificar idempotência concorrente` |
| `refactor` | Estrutura sem alteração funcional | `refactor(api): separar consultas de carteira` |
| `perf` | Desempenho medido | `perf(positions): reduzir consultas por carteira` |
| `chore` | Dependências e manutenção | `chore(dev): configurar ambiente Python` |
| `ci` | Verificação contínua | `ci: validar API e frontend em pull requests` |

Formato: `tipo(escopo opcional): verbo e resultado específico`. Assunto objetivo,
preferencialmente até 72 caracteres, sem ponto final. Corpo explica motivo,
decisões relevantes e validação quando necessário. Mudança incompatível usa `!`
e um rodapé `BREAKING CHANGE:` com orientação de migração.

## Um ciclo por incremento

1. Trabalhe na etapa ativa e confira `git status` para preservar trabalho existente.
2. Implemente um bloco completo e execute as verificações pertinentes.
3. Atualize `docs/STATUS.md` com escopo, evidência, pendências e próximo passo.
4. Revise o diff, dados sensíveis e `git diff --check`.
5. Adicione explicitamente os arquivos do bloco e crie o commit convencional.
6. Execute `git push` para a branch de trabalho; confirme o SHA remoto.
7. Informe o avanço com link ao commit. O PR reúne os incrementos para revisão.

Não crie commits vazios para simular progresso. Um bloco pode ser parte da
Etapa 1 sem concluí-la. As três etapas são produção do produto; commits não são
etapas adicionais. Nunca marque um push como concluído se o servidor o rejeitar.

## Branches, dependências e revisão

- Use uma branch por tarefa, por exemplo `feat/etapa-1-ingestao-autor`;
  delimite arquivos e contratos antes de trabalhar em paralelo.
- A integração padrão é em `main`. Para trabalho que depende de PR ainda aberto,
  use sua branch como base e declare `Depende de #<número>`; abra o PR contra
  essa base enquanto a dependência não for integrada.
- Não faça push direto em `main`, force push, reescrita de histórico publicado,
  auto-merge nem merge pelo agente. Preserve alterações de colegas e resolva
  conflitos conferindo o resultado com os responsáveis.
- Use título convencional e preencha
  [o template](.github/pull_request_template.md): problema/comportamento, etapa e
  requisitos, dependências, como conferir, comandos/resultados/SHA, migrações,
  limites e capturas reais quando houver UI.
- Atualize os contextos afetados mantendo inventário real **e os três roteiros**;
  atualize STATUS/HANDOFF/contratos quando pertinente.
- Durante implementação ou validação pendente, mantenha o PR em rascunho.
  Para solicitar revisão, confira o diff, o SHA remoto e os jobs `api`, `web`
  e `native` desse commit. Peça revisão de `DaviTosatti` no PR; se não tiver
  permissão para atribuir revisor, informe a Davi o link, SHA e limitações.
- Somente Davi autoriza a integração final. Autor/assistente não aprova o próprio
  PR; silêncio não é autorização. Alterações posteriores exigem nova conferência
  e aprovação. Documentar essas regras não configura proteção remota de branch.

## Evidência de validação

Execute checks proporcionais à mudança e registre o ambiente/comando/resultado.
Para documentação isolada, confira links, fatos e `git diff --check`; não é
necessário repetir testes de código que não mudou. Para código, consulte
`scripts/check.sh` e os workflows: Mypy cobre o motor, testes de integração usam
bancos isolados e compatibilidade Windows exige evidência nativa.

Não copie resultados de um SHA antigo como prova de um novo commit. Declare
checks não executados, bloqueios e falhas preexistentes com evidência. Dados,
logs, capturas e arquivos compartilhados devem ser sintéticos ou autorizados e
não conter segredos, sessões ou dados financeiros pessoais.

## English

Use Conventional Commits, one coherent change per commit. Verify changes, update
the progress record, inspect staged content, commit, push to the working branch
and verify its remote SHA. Product stages are distinct from individual commits.
