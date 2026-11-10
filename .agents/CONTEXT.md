# Contexto de `.agents/` — Governança de Skills e Agentes Multi-LLM

## 1. Missão e Objetivo (Goal)
O diretório `.agents/` é o centro de engenharia de contexto e capacitação de agentes autônomos de IA (Antigravity, Claude Code, OpenAI Codex) no repositório do Investment Research Hub.
Sua missão é fornecer um ecossistema padronizado de **skills de desenvolvimento** (procedimentos técnicos avançados, checklists de qualidade e boas práticas de código) que possam ser invocadas de maneira idêntica por qualquer modelo de linguagem líder de mercado, permitindo que os agentes operem com rigor de engenharia sem alterar as regras de negócio do Hub.
> *Nota Fundamental: As skills de desenvolvimento presentes aqui NÃO se confundem com as 23 skills de negócio financeiro do produto (S01 a S23) descritas na matriz de requisitos.*

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Skills de Engenharia Padronizadas (`skills/` — 26 skills ativas):**
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
  - Espelho físico das skills e checklists sincronizados por script com integridade SHA-256 fixada em `skills-lock.json`.

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

## 4. Contratos de Invocação Multi-LLM
- **Google Antigravity e OpenAI Codex:**
  - Leem automaticamente as definições presentes em `.agents/skills/<nome-da-skill>/SKILL.md`.
  - As diretrizes globais do projeto vêm de `AGENTS.md`.
- **Anthropic Claude Code:**
  - Lê a instrução mestre via `CLAUDE.md` (que aponta para `AGENTS.md`).
  - Carrega as skills pelo diretório espelho `.claude/skills/<nome-da-skill>/SKILL.md`.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Registro de documentação de procedimento e validação para as 7 skills de negócio da Etapa 1.
  - Passo de verificação criptográfica das skills de desenvolvimento (`python scripts/sync_agent_skills.py --check`) integrado como job no GitHub Actions (`.github/workflows/verify.yml`).
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Documentação dos procedimentos de verificação formal e benchmarks para os 12 motores da Etapa 2.
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
  *(O comando deve retornar código de saída 0 e exibir `26 skills; ok`)*.
