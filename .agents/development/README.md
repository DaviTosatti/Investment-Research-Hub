# Agentes de desenvolvimento do Hub

Configuração específica deste projeto, sem alterar preferências globais do Codex.
Estes papéis não são as 23 skills de negócio da aplicação.

| Papel | Escopo | Saída verificável |
| --- | --- | --- |
| Integração | Contratos, API, contabilidade, commits/push e STATUS | Incrementos funcionais, testes, registro e PR |
| Interface | `apps/web` | UI com serviços reais, testes de formulário/estado, tipos e build |
| Documentação | Documentos de escopo, matriz e decisões | Três etapas e requisitos preservados, com evidências separadas de propostas |
| Revisão financeira | Cálculos, invariantes e concorrência | Casos independentes, reproduções de falhas e regressões |

Nesta sessão, documentação e interface usaram subagentes `gpt-6.1-sol` com
esforço `xhigh`; a revisão numérica usou `gpt-6-astra` com `xhigh`. A identidade
exata do modelo do agente principal não foi exposta por uma ferramenta, portanto
não é inferida. A disponibilidade dos modelos deve ser revalidada ao retomar.

Antes de delegar, fixe contratos e arquivos exclusivos. Agentes implementam e
informam arquivos/checks/limites; a integração revisa, executa o necessário e
publica. Preserve trabalho existente em retomadas e verifique o estado real
dos processos após reinicialização. Não alegue trabalho em segundo plano sem
tarefa ativa confirmada. Leia `docs/HANDOFF.md` para a próxima dependência.

English: project-local engineering roles, separate from business skills. Use
bounded write scopes, shared contracts and independent numerical regressions.
