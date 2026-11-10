# Metodologia de Contexto (ICM) — Monorepo Investment Research Hub

Este documento define a governança de contexto para agentes de IA (Antigravity, Claude, Codex) e desenvolvedores humanos no repositório do **Investment Research Hub**, baseada no modelo ICM (Information/Context Management - *Menos Agentes, Mais Contexto*) e nas referências aprovadas do projeto ([CERC ICM](https://building.cerc.com/blog/icm-menos-agentes-mais-contexto/) e [Sementis-IFSP-Pirituba](https://github.com/PHenrique07/Sementis-IFSP-Pirituba)).

---

## 1. Princípios Fundamentais

1. **Contexto junto ao trabalho:** Instruções, contratos, invariantes e status vivem versionados ao lado do código que governam, em arquivos `CONTEXT.md`.
2. **Sem camadas desnecessárias de agentes:** Um mesmo agente é capaz de pesquisar, planejar, codificar e testar em diferentes pastas. O caminho de contexto guia o agente; não se criam enxames de subagentes para tarefas que uma árvore bem documentada resolve.
3. **Mimetismo e preservação estrita:** Seguir rigorosamente os padrões já existentes. Não introduzir bibliotecas, frameworks ou reestruturações não solicitadas.
4. **Três etapas imutáveis:** O plano de entrega do Hub tem exatamente 3 etapas descritas em `docs/IMPLEMENTATION_PLAN.md` e 23 skills de negócio em `docs/REQUIREMENTS_MATRIX.md`. Documentação nunca simula conclusão de módulo.
5. **Diferença entre Skills e Dicas de Contexto:**
   - **Dica/Regra de Contexto:** Instrução pontual (ex.: "Use Decimal em cálculos monetários", "Não aceite caixa negativo"). Fica no `CONTEXT.md` local.
   - **Skill de Desenvolvimento (`.agents/skills`):** Procedimento técnico completo, estruturado e recorrente com passos de execução e validação (ex.: TDD, Code Review, Performance Optimization).
   - **Skill de Negócio (S01–S23):** Funcionalidade do produto financeiro (ex.: Carteiras, Valuation, Risco, Backtesting, Comitê IA).

---

## 2. A Arquitetura de Camadas (Layers 0 a 5)

| Camada | Escopo | Arquivo(s) | Função Principal |
| :--- | :--- | :--- | :--- |
| **Layer 0 — Identidade Global** | Todo o repositório | `AGENTS.md`, `CLAUDE.md` | Regras globais invioláveis, limites operacionais, conduta, roteamento para as áreas. |
| **Layer 1 — Área** | Macro-módulos | `apps/CONTEXT.md`, `packages/CONTEXT.md`, etc. | Roteia para as subpastas concretas, explica sinergias e limites da área. |
| **Layer 2 — Contrato Local** | Subárea de trabalho | `apps/api/CONTEXT.md`, `packages/engines/CONTEXT.md`, etc. | Objetivo (Goal), O Que Existe Hoje (Checklist real), Regras Locais, Contratos I/O, Próximas Etapas e Fora de Escopo. |
| **Layer 3 — Referências** | Documentos estáveis | `docs/*.md`, `.agents/references/*.md` | Documentos consultados sob demanda (Ex: `docs/API_CONTRACT.md`, `docs/VISUAL_REFERENCES.md`). |
| **Layer 4 — Arquivos da Tarefa** | Implementação | Código-fonte, migrações, testes | Arquivos lidos e modificados durante a execução do incremento. |
| **Layer 5 — Invariantes & Verificação** | Validação final | Seção de Invariantes em `CONTEXT.md` | Comandos reais de teste, lint, checagem de tipos e integridade contábil. |

---

## 3. Estrutura Obrigatória de um `CONTEXT.md`

Todo arquivo `CONTEXT.md` de subárea deve conter obrigatoriamente:

```markdown
# Contexto: <Nome da Pasta / Módulo>

## 1. Missão e Objetivo (Goal)
[Descrição concisa do papel deste módulo no ecossistema e seu propósito de negócio e técnico]

## 2. O Que Existe Efetivamente (Checklist Real)
[Checklist [x] com arquivos, rotas, tabelas ou componentes REALMENTE implementados e testados]
- [x] Item real existente

## 3. Regras de Negócio e Invariantes Locais
[Regras rígidas da pasta, invariantes financeiras, de segurança ou de dados]

## 4. Contratos de Interface (Inputs, Process, Outputs)
[Estruturas de dados, contratos HTTP, modelos Pydantic/SQLAlchemy ou props React que esta pasta consome e entrega]

## 5. Roteiro por Etapas (O que devemos ter no final)
- [ ] **Etapa 1 — Fundação:** [Pendências concretas da etapa ativa]
- [ ] **Etapa 2 — Análise Avançada:** [Entregas da etapa futura 2]
- [ ] **Etapa 3 — Comitê IA & Operação:** [Entregas da etapa futura 3]

## 6. O que FICA FORA de Escopo
[Limites claros do que NÃO deve ser implementado ou colocado nesta pasta]

## 7. Verificação e Comandos
[Comandos exatos para validar alterações nesta pasta: testes, linters, checagem de tipos]
```

---

## 4. Governança das Skills de Desenvolvimento Multi-LLM

- **Fonte canônica:** `.agents/skills/`. Qualquer nova skill ou alteração deve ser feita exclusivamente nesta pasta.
- **Espelho automático:** `.claude/skills/` e `.claude/references/` são espelhos gerados para compatibilidade com o Claude Code.
- **Sincronização:** Sempre que alterar `.agents/skills/` ou referências, execute:
  ```bash
  python scripts/sync_agent_skills.py
  ```
  O script gera/atualiza o espelho e recalcula o `skills-lock.json` com o hash de integridade de cada skill. No CI, use `python scripts/sync_agent_skills.py --check`.
- **Roteamento de agentes:** Antigravity e Codex leem `.agents/rules` e `.agents/skills`; Claude Code lê `CLAUDE.md` e `.claude/skills`.
