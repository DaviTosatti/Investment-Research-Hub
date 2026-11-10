# Contexto de `.agents/` — Governança de Skills e Agentes Multi-LLM

## 1. Missão e Objetivo (Goal)
O diretório `.agents/` é o centro de engenharia de contexto e capacitação de agentes autônomos de IA (Antigravity, Claude Code, OpenAI Codex) no repositório do Investment Research Hub.
Sua missão é fornecer **skills de desenvolvimento** (procedimentos técnicos, checklists e práticas de código) reutilizáveis pelos clientes compatíveis, preservando as regras do Hub. Descoberta e invocação dependem do cliente/configuração; a árvore de arquivos não comprova carregamento automático em todos os modelos.
> *Nota Fundamental: As skills de desenvolvimento presentes aqui NÃO se confundem com as 23 skills de negócio financeiro do produto (S01 a S23) descritas na matriz de requisitos.*

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Skills de Engenharia Padronizadas (`skills/` — 26 diretórios com `SKILL.md`):**
  - **Arquitetura e Design:** `api-and-interface-design`, `context-engineering`, `spec-driven-development`, `source-driven-development`.
  - **Qualidade e Testes:** `test-driven-development`, `code-review-and-quality`, `code-simplification`, `constraint-driven-development`, `doubt-driven-development`.
  - **Execução e Entrega:** `planning-and-task-breakdown`, `incremental-implementation`, `debugging-and-error-recovery`, `git-workflow-and-versioning`, `ci-cd-and-automation`, `shipping-and-launch`, `deprecation-and-migration`.
  - **Domínio Técnico Especializado:** `frontend-ui-engineering`, `browser-testing-with-devtools`, `performance-optimization`, `observability-and-instrumentation`, `security-and-hardening`.
  - **Refinamento e Metodologia:** `idea-refine`, `interview-me`, `documentation-and-adrs`, `using-agent-skills`.
  - **Engenharia Reversa:** `reverse-engineer-anything` (do ecossistema REA de @morluto).
- [x] **Checklists Técnicos Compartilhados (`references/`):**
  - `accessibility-checklist.md`: Critérios de acessibilidade WCAG para a interface web.
  - `definition-of-done.md`: Critérios formais para considerar um incremento pronto para commit.
  - `observability-checklist.md`: Verificação de logs, métricas e rastreabilidade.
  - `orchestration-patterns.md`: Padrões de orquestração de subagentes e tarefas.
  - `performance-checklist.md`: Checklist para otimização de consultas e renderização.
  - `security-checklist.md`: Auditoria de segurança OWASP, injeções e proteção de segredos.
  - `testing-patterns.md`: Padrões e pirâmide de testes unitários, integração e propriedades.
- [x] **Definição de Perfis Locais de Engenharia (`development/README.md`):**
  - Guia dos papéis internos do Hub: Integração, Interface, Documentação e Revisão Financeira.
- [x] **Espelho Gerado para Claude Code (`.claude/`):**
  - Espelho físico gerado unidirecionalmente por script. Na base auditada, espelhos correspondem às origens, mas cinco hashes de `skills-lock.json` divergem; o check retorna exit 1.

Fontes: [catálogo local](skills), [perfis](development/README.md), [sincronizador](../scripts/sync_agent_skills.py), [lockfile](../skills-lock.json) e [auditoria F09](../docs/CONTEXT_PLAN_COMPARISON.md). Este inventário é da base; a revisão dos contextos não corrige lockfile/espelhos nem valida invocação nos clientes.

## 3. Regras de Negócio e Governança das Skills
- **Fonte Canônica Única (`.agents/`):**
  - Toda e qualquer edição de skills ou criação de novos procedimentos deve ocorrer exclusivamente em `.agents/skills/`.
  - Proibido editar diretamente os arquivos dentro de `.claude/skills/` (estes são artefatos gerados pelo sincronizador).
- **Sincronização Obrigatória:**
  - Após qualquer alteração em `.agents/skills/`, deve-se rodar obrigatoriamente:
    ```bash
    python scripts/sync_agent_skills.py
    ```
    Isso replica as skills para `.claude/skills/` e atualiza o lockfile `skills-lock.json`.
- **Limites da Skill de Engenharia Reversa (`reverse-engineer-anything`):**
  - A skill REA serve exclusivamente para desconstruir ou extrair lógicas de artefatos externos entregues como evidência (ex: descompilar binários de fornecedores, inspecionar pacotes de dados). Ela nunca deve ser usada para analisar os fontes ordinários do próprio monólito do Hub.
- **Não Substituição do Contexto Local:**
  - Skills fornecem métodos de trabalho (como conduzir um TDD ou Code Review). Regras específicas da pasta (como "use Decimal" ou "não aceite short selling") pertencem aos arquivos `CONTEXT.md` locais.
  - Promptx §1 orienta frentes paralelas independentes com contratos/arquivos exclusivos e um responsável pela integração. Registrar somente agentes/modelos realmente utilizados; os perfis locais não provam disponibilidade de ferramentas na sessão.

## 4. Contratos de Invocação Multi-LLM
- **Google Antigravity e OpenAI Codex:**
  - A fonte preparada para descoberta é `.agents/skills/<nome-da-skill>/SKILL.md`; confirmar suporte e configuração do cliente antes de afirmar carregamento automático.
  - As diretrizes globais do projeto vêm de `AGENTS.md`.
- **Anthropic Claude Code:**
  - `CLAUDE.md` aponta para `AGENTS.md`; o espelho preparado é `.claude/skills/<nome-da-skill>/SKILL.md`.
  - A presença desses arquivos não é evidência de uma execução/invocação real neste cliente; verificar a descoberta na instalação usada.

## 5. Roteiro por Etapas (Ao fim das etapas)

Escopo de produto no [plano](../docs/IMPLEMENTATION_PLAN.md) e na [matriz](../docs/REQUIREMENTS_MATRIX.md); skills de engenharia não concluem skills financeiras.

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Procedimentos, referências, wrappers/ferramentas executáveis e avaliações das sete skills S01/S02/S12/S03/S07/S21/S23, ligados a dados/serviços/telas reais, fontes, versões, histórico e limites; não apenas documentação.
  - Corrigir com rastreabilidade os cinco hashes divergentes antes de tornar a integridade um gate verde; comprovar descoberta/invocação nos clientes efetivamente usados.
  - Passo de verificação criptográfica das skills de desenvolvimento (`python scripts/sync_agent_skills.py --check`) integrado como job no GitHub Actions (`.github/workflows/verify.yml`).
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Documentação dos procedimentos de verificação formal e benchmarks dos motores que atendem às 12 skills da Etapa 2, ampliando a linha de base exigida na Etapa 1.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Conclusão das diretrizes do Comitê de IA com garantia de que os prompts dos agentes especialistas operam de forma isolada e rastreável.

## 6. O Que Fica Fora de Escopo
- Não adicionar skills que modifiquem automaticamente arquivos de produção sem passar por teste humano ou de integração.
- Não versionar chaves de API, credenciais ou tokens de LLMs dentro de `.agents/`.

## 7. Verificação e Comandos
- **Validar integridade e sincronismo das skills multi-LLM:**
  ```bash
  python scripts/sync_agent_skills.py --check
  ```
  Resultado observado na base e repetido nesta revisão: exit 1, `skills-lock.json desatualizado`; a auditoria F09 identifica cinco hashes divergentes. `26 skills; ok`/exit 0 é o resultado esperado somente após correção, não aprovação atual. O modo `--check` não grava arquivos.
