# Metodologia de contexto (ICM)

Inspirada em [ICM: menos agentes, mais contexto](https://building.cerc.com/blog/icm-menos-agentes-mais-contexto/) (CERC) e no padrão do repositório Sementis-IFSP-Pirituba.

| Camada | Arquivo | Função |
| --- | --- | --- |
| 0 — identidade | `AGENTS.md` (`CLAUDE.md` aponta para ele) | Regras globais e roteamento |
| 1 — área | `CONTEXT.md` de `apps/`, `packages/`, `docs/`… | Direciona à subárea |
| 2 — contrato local | `CONTEXT.md` da pasta | O que existe, padrões, pendências, fora de escopo |
| 3 — referências | `docs/*.md`, `.agents/references/` | Convenções estáveis, citadas e não copiadas |
| 4 — tarefa | arquivos concretos | Só o necessário |
| 5 — invariantes | seção "Verificação" | Checagem ao concluir |

## Formato do `CONTEXT.md`

1. **Escopo** (1–2 linhas).
2. **O que existe hoje** — checklist `[x]` só do que existe de fato.
3. **Padrões** locais.
4. **Ao fim das etapas** — checklist `[ ]` por etapa (1, 2, 3) conforme `IMPLEMENTATION_PLAN.md`.
5. **Fora de escopo** e **Verificação**.

## Manutenção

- Atualize o `CONTEXT.md` no mesmo commit que cria/remove arquivos da pasta; marque `[x]` apenas com evidência.
- Não copie regras: aponte para a fonte. Sobe de nível só se valer para várias subpastas.
- Skills (`.agents/skills`) são procedimentos recorrentes; dicas simples vão no contexto.
