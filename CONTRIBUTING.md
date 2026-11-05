# Contribuição e publicação incremental

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

## English

Use Conventional Commits, one coherent change per commit. Verify changes, update
the progress record, inspect staged content, commit, push to the working branch
and verify its remote SHA. Product stages are distinct from individual commits.
