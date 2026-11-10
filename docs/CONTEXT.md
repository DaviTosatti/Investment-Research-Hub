# Contexto de `docs/` — Documentação Técnica, Planos e Arquitetura

## 1. Missão e Objetivo (Goal)
O diretório `docs/` é o repositório central da verdade de especificação, planejamento temporal, status operacional e decisões de arquitetura do Investment Research Hub.
Sua missão é fornecer para engenheiros humanos e modelos de IA o mapa completo dos requisitos institucionais do Hub (preservados integralmente a partir da especificação original `Promptx.txt`), registrando com evidências comprovadas o progresso real do sistema e garantindo que nenhuma funcionalidade seja considerada concluída sem verificação de ponta a ponta.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Documentos de Governança e Especificação:**
  - `reference/Promptx.txt`: A especificação integral e inalterada do Hub (edição de 04/11/2026). Serve como fonte primária de verdade.
  - `IMPLEMENTATION_PLAN.md`: O plano de execução estritamente dividido em 3 etapas sequenciais (Etapa 1: Fundação; Etapa 2: Análise Avançada; Etapa 3: Comitê IA).
  - `REQUIREMENTS_MATRIX.md`: A matriz exaustiva com as 23 skills de negócio (S01 a S23), 23 páginas funcionais (P01 a P23), 10 skills do núcleo profissional e 56 casos normativos de teste (T01 a T56).
  - `STATUS.md`: Registro vivo de entregas auditadas com links para commits de produção, hashes de artefatos e comandos executados.
  - `HANDOFF.md` e `LOCAL_HANDOFF.md`: Guias de transição entre sessões de desenvolvimento e orientações para retomada no ambiente local do usuário.
  - `metodologia-contexto.md`: Especificação da arquitetura ICM (menos agentes, mais contexto) adotada no repositório.
- [x] **Documentos de Arquitetura e Engenharia:**
  - `API_CONTRACT.md`: Contratos HTTP detalhados de endpoints, schemas de payload, parâmetros de paginação e cabeçalhos de segurança.
  - `COMPUTE_ARCHITECTURE.md`: Diretrizes da arquitetura computacional dos motores de cálculo (estratégia Python first, critérios para adoção de Rust/Julia).
  - `PERFORMANCE_BASELINE.md`: Metodologia de medição e registro de tempos de processamento e limites operacionais.
  - `DATA_CATALOG.md`: Catálogo dos modelos de dados relacionais e eventos do ledger contábil.
  - `DECISIONS.md`: Registro de Decisões de Arquitetura (ADRs) fundamentando as escolhas técnicas tomadas.
  - `MODEL_REGISTRY.md`: Registro dos motores numéricos e modelos estatísticos suportados.
  - `VISUAL_REFERENCES.md`: Critérios estéticos e as 11 imagens de referência aprovadas para guiar a identidade fintech escura.
  - `WINDOWS.md`: Documentação técnica do porte e execução nativa em sistemas operacionais Windows.

## 3. Regras de Negócio e Invariantes da Documentação
- **Preservação Rígida das 3 Etapas:** É expressamente vedado alterar, fundir ou eliminar as três etapas fundamentais do plano ou as 23 skills de negócio da matriz.
- **Diferenciação Estrita entre Realidade e Proposta:** Documentação descreve o estado implementado ou aponta expressamente que se trata de uma especificação futura. Arquivos de texto, interfaces mockadas ou declarações em chat não transformam uma funcionalidade em "concluída".
- **Evidências no STATUS:** Cada entrega lançada no `STATUS.md` deve conter obrigatoriamente: identificador do incremento (ex: `E1.12`), descrição da mudança, validações reais executadas (comandos e saídas) e referência rastreável (hash do commit ou link de ação).
- **Inviolabilidade do Promptx.txt:** O arquivo `docs/reference/Promptx.txt` é de somente-leitura e não deve ser modificado, servindo como auditor de conformidade do projeto.

## 4. Estrutura de Referências e Consulta
- Para arquitetura de motores e decisões numéricas: consulte `docs/COMPUTE_ARCHITECTURE.md`.
- Para contratos de rede e payloads: consulte `docs/API_CONTRACT.md`.
- Para layout, paleta de cores e componentes visuais: consulte `docs/VISUAL_REFERENCES.md`.
- Para manutenção da metodologia de contexto: consulte `docs/metodologia-contexto.md`.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Atualização do `STATUS.md` e `REQUIREMENTS_MATRIX.md` com evidências da integração completa das 7 skills iniciais (S01, S02, S12, S03, S07, S21, S23).
  - Registro formal dos contratos de ingestão de dados (`/sources`, `/imports`, `/snapshots`) em `API_CONTRACT.md`.
  - Manual operacional de backup e restauração adicionado à documentação.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Registro detalhado dos 12 novos motores analíticos em `MODEL_REGISTRY.md`.
  - Linha de base e benchmarks computacionais comparativos registrados em `PERFORMANCE_BASELINE.md`.
  - Documentação das regras fiscais e vigências tributárias brasileiras em manual dedicado.
- [ ] **Etapa 3 — Comitê IA, Colaboração, Monitoramento e Operação Completa:**
  - Documentação completa do fluxo do Comitê de IA (S22), detalhando prompts dos especialistas, auditoria e separação de decisões.
  - Guia definitivo de restauração a frio e operação supervisionada do Hub.

## 6. O Que Fica Fora de Escopo
- Não documentar como "funcional" ou "pronto" nenhum recurso que não possua testes automatizados passando.
- Não introduzir notas ou documentos paralelos que contradigam os preceitos do `Promptx.txt`.

## 7. Verificação
- **Checagem de Links e Diffs:**
  Garantir que todos os links relativos em arquivos markdown apontem para documentos existentes e que não haja links quebrados.
