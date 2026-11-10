# Contexto de `docs/` — Documentação Técnica, Planos e Arquitetura

## 1. Missão e Objetivo (Goal)
O diretório `docs/` é o repositório central da verdade de especificação, planejamento temporal, status operacional e decisões de arquitetura do Investment Research Hub.
Sua missão é fornecer para engenheiros humanos e modelos de IA o mapa completo dos requisitos institucionais do Hub (preservados integralmente a partir da especificação original `Promptx.txt`), registrando com evidências comprovadas o progresso real do sistema e garantindo que nenhuma funcionalidade seja considerada concluída sem verificação de ponta a ponta.

## 2. O Que Existe Efetivamente (Checklist Real)
- [x] **Documentos de Governança e Especificação:**
  - `reference/Promptx.txt`: A especificação integral e inalterada do Hub (edição de 04/11/2026). Serve como fonte primária de verdade.
  - `IMPLEMENTATION_PLAN.md`: O plano de execução estritamente dividido em 3 etapas sequenciais (Etapa 1: Fundação; Etapa 2: Análise Avançada; Etapa 3: Comitê IA).
  - `REQUIREMENTS_MATRIX.md`: Contratos das 23 skills (S01–S23), 23 páginas previstas (P01–P23), 10 skills do núcleo profissional e 56 casos normativos (T01–T56), com uma tabela separada de evidências do recorte implementado.
  - `STATUS.md`: Registro de entregas, comandos, resultados, commits/runs e limitações; não é certificado de produção ou conclusão integral.
  - `HANDOFF.md` e `LOCAL_HANDOFF.md`: Guias de transição entre sessões de desenvolvimento e orientações para retomada no ambiente local do usuário.
  - `metodologia-contexto.md`: Especificação da arquitetura ICM (menos agentes, mais contexto) adotada no repositório.
  - `STAGE_1_AUDIT.md` e `CONTEXT_PLAN_COMPARISON.md`: Auditorias datadas de cobertura e de divergências dos contextos; resultados históricos não incorporam automaticamente trabalho posterior.
- [x] **Documentos de Arquitetura e Engenharia:**
  - `API_CONTRACT.md`: Contratos HTTP detalhados de endpoints, schemas de payload, parâmetros de paginação e cabeçalhos de segurança.
  - `COMPUTE_ARCHITECTURE.md`: Diretrizes da arquitetura computacional dos motores de cálculo (estratégia Python first, critérios para adoção de Rust/Julia).
  - `PERFORMANCE_BASELINE.md`: Cargas e protocolo de medição propostos; ainda sem benchmark representativo medido no registro da base.
  - `DATA_CATALOG.md`: Contratos de origem/normalização/qualidade e fontes propostas; identifica avaliações/operações manuais persistidas, sem provedor externo integrado/validado na base.
  - `DECISIONS.md`: Registro de Decisões de Arquitetura (ADRs) fundamentando as escolhas técnicas tomadas.
  - `MODEL_REGISTRY.md`: Método inicial do ledger `average-cost-brl/1.0.1` e contratos dos demais métodos planejados, não catálogo de motores já suportados.
  - `VISUAL_REFERENCES.md`: Critérios estéticos e as 11 imagens de referência aprovadas para guiar a identidade fintech escura.
  - `WINDOWS.md`: Documentação técnica do porte e execução nativa em sistemas operacionais Windows.

Fontes: [plano](IMPLEMENTATION_PLAN.md), [matriz](REQUIREMENTS_MATRIX.md), [catálogo de dados](DATA_CATALOG.md), [registro de modelos](MODEL_REGISTRY.md), [protocolo de desempenho](PERFORMANCE_BASELINE.md) e [comparação dos contextos](CONTEXT_PLAN_COMPARISON.md). A revisão preserva a base anterior à integração de importação e não promove o trabalho corrente a concluído.

## 3. Regras de Negócio e Invariantes da Documentação
- **Preservação Rígida das 3 Etapas:** É expressamente vedado alterar, fundir ou eliminar as três etapas fundamentais do plano ou as 23 skills de negócio da matriz.
- **Diferenciação Estrita entre Realidade e Proposta:** Documentação descreve o estado implementado ou aponta expressamente que se trata de uma especificação futura. Arquivos de texto, interfaces mockadas ou declarações em chat não transformam uma funcionalidade em "concluída".
- **Evidências no STATUS:** Cada entrega lançada no `STATUS.md` deve conter obrigatoriamente: identificador do incremento (ex: `E1.12`), descrição da mudança, validações reais executadas (comandos e saídas) e referência rastreável (hash do commit ou link de ação).
- **Inviolabilidade do Promptx.txt:** O arquivo `docs/reference/Promptx.txt` é de somente-leitura e não deve ser modificado, servindo como auditor de conformidade do projeto.
- **Coordenação e Evidência:** Promptx §1 prevê um integrador e frentes paralelas com arquivos exclusivos; ICM orienta a consulta, sem eliminar essa distribuição. Não alegar agentes/modelos ou carregamento de skills sem evidência da sessão efetiva.

## 4. Estrutura de Referências e Consulta
- Para arquitetura de motores e decisões numéricas: consulte `docs/COMPUTE_ARCHITECTURE.md`.
- Para contratos de rede e payloads: consulte `docs/API_CONTRACT.md`.
- Para layout, paleta de cores e componentes visuais: consulte `docs/VISUAL_REFERENCES.md`.
- Para manutenção da metodologia de contexto: consulte `docs/metodologia-contexto.md`.
- Entrada: requisito original, código e execução observados; processo: reconciliar afirmações com essas fontes e distinguir baseline de proposta; saída: contratos/pendências e evidências datadas, sem converter texto em prova funcional.

## 5. Roteiro por Etapas (Ao fim das etapas)

- [ ] **Etapa 1 — Fundação, Experiência Visual, Dados e Acompanhamento:**
  - Atualização do `STATUS.md` e `REQUIREMENTS_MATRIX.md` com evidências da integração completa das 7 skills iniciais (S01, S02, S12, S03, S07, S21, S23).
  - Registro formal dos contratos de ingestão de dados (`/sources`, `/imports`, `/snapshots`) em `API_CONTRACT.md`.
  - Documentar identidade/proveniência, fontes reais e cobertura, qualidade/quarentena, disponibilidade/revisões, reconciliação/correção, serviços de mercado/fundamentos/macro/aprendizado, diário/metas/performance e seus limites efetivamente implementados.
  - Manual operacional de backup/restauração com evidência de execução em destino vazio para banco e armazenamento entregues; manual sozinho não satisfaz o portão.
  - Manifesto dos motores e primeira linha de base efetivamente medida em `PERFORMANCE_BASELINE.md`, com ambiente, volume, componentes, memória, variação e limitações.
  - Evidências de jobs duráveis/reinício/cancelamento, wrappers/MCP e relatórios, procedimentos/ferramentas/avaliações das sete skills, duas contas autorizadas, jornada A e recortes B/F, revisão visual nas quatro larguras e acessibilidade.
- [ ] **Etapa 2 — Análise Avançada, Classes de Ativos e Estratégias:**
  - Registro dos métodos/motores que atendem às 12 skills avançadas em `MODEL_REGISTRY.md`; a contagem de skills não impõe 12 motores independentes.
  - Ampliação da linha de base da Etapa 1 e benchmarks comparativos dos novos motores em `PERFORMANCE_BASELINE.md`.
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
  Conferir também os destinos citados contra código/comandos e preservar os três roteiros; links válidos não comprovam a veracidade do conteúdo nem execução de testes.
