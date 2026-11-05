# Plano de implementação — exatamente três etapas

Atualizado em 05/11/2026. Fonte: Promptx.txt §§1–13, edição 04/11/2026. Planejamento de cobertura integral; código e testes precisam de verificação pelo integrador antes de qualquer mudança para validado. Etapas 2 e 3 permanecem não iniciadas.

## Organização e dependências comuns

Monólito modular: frontend, API e, quando implementado, worker em processos próprios, com contratos de domínio e motores compartilhados. A integração controla alterações transversais e commits; frentes paralelas têm arquivos e contratos delimitados. Documentação não equivale a implementação. Caminhos ainda não verificados na matriz são propostas.

Autenticação, autoria, titularidade, auditoria, persistência, histórico, acessibilidade e testes começam na etapa 1 e evoluem nas seguintes. Contratos de motores separam método financeiro, implementação computacional e configuração de execução. Lockfiles e migrações preservam instalação e dados. Não criar crates Rust, módulos Julia ou árvores vazias apenas para demonstrar arquitetura.

Antes de integrar: revisar diferenças, executar as verificações pertinentes e checar segredos/dados pessoais. O integrador publica cada incremento verificado com Conventional Commits. Registrar comando, resultado e limitações em STATUS/HANDOFF; não inventar execução, benchmark, modelo ou fonte.

## Etapa 1 — Fundação, experiência visual, dados e acompanhamento

**Skills (7): S01, S02, S12, S03, S07, S21, S23.**

| Bloco interno | Entrega e dependência | Evidência exigida |
| --- | --- | --- |
| Inspeção e contratos | Inventário real, fonte de escopo, modelo de grupo/titulares, contratos e matriz. ZIP das skills originais ausente deve ser registrado. | Arquivos examinados; decisões e limitações datadas, sem presumir recursos existentes. |
| Primeiro incremento integrado | Next.js/TS fintech escuro; FastAPI/Pydantic/SQLAlchemy/Alembic/PostgreSQL; login/sessões e admin/member/viewer; titulares, carteiras, contas, instrumentos; ledger Decimal balanceado e imutável para deposit/withdrawal/buy/sell/dividend/fee/tax/split; idempotência; preços manuais persistidos; posições/caixa derivados; CSV básico. | Persistência real; autorização e titularidade; T01–T04, T12, T29–T30, T38 e T41 nos recortes aplicáveis; custo/mercado separados e mercado indisponível sem cotação; build/tipos e revisão visual. Este conjunto é um incremento, não conclusão de skills. |
| Identidade, ingestão e qualidade | Emissor/instrumento/listagem; snapshots, fonte/tempo e revisões; fontes reais acessíveis; CSV/XLSX com mapeamento, prévia e reconciliação; originais preservados. | Reimportação sequencial/concorrente e entre arquivos, unidades/períodos, nulos, quarentena, correção rastreável e cobertura efetiva do provedor. |
| Contabilidade e acompanhamento | Ampliar eventos conforme integridade dos ativos suportados; saldos iniciais identificados, transferências, câmbio e proventos; custo, resultado, patrimônio e performance canônicos. | T01–T07, T15, T21, T25–T26; conciliação independente; TWR/MWR ou aproximação nomeada quando aplicável. Splits são contabilizados aqui, não adiados até S13. |
| Pesquisa e aprendizado | S02 Mercado/watchlists; S12 auditoria; S03 fundamentos/TTM/setores; S07 macro; S23 trilhas/glossário/indicadores; diário/teses e comentários básicos. | Fonte e datas verificáveis, disponibilidade histórica, banco/FII sem métricas inadequadas, exemplos executados e tese versionada. |
| Relatórios, contratos públicos e operação | S21 motor/templates funcionais, formatos previstos na cobertura inicial; HTTP /api/v1 e MCP inicial; wrappers; um mecanismo de jobs; configuração e recuperação inicial. | Igualdade tela/arquivo, abertura/renderização dos formatos entregues, artefatos autorizados, jobs persistidos, reinício, backup e restauração demonstráveis. CSV básico sozinho não conclui S21. |
| Integração da etapa | Navegação e páginas da cobertura, demonstrações identificadas, erros/ausências, manifesto dos motores e primeira linha de base medida. | Jornada A e parte de B/F correspondente; duas contas autorizadas; sete skills com procedimentos, ferramentas e avaliações; medições reais. |

Páginas-base: P01, P02, P03, P04, P08, P10, P11, P12, P19, P21, P22 e P23. Partes futuras de uma página não tornam pronta sua cobertura atual.

**Portão da etapa:** dois usuários compartilham dados permitidos com autoria e titulares distintos; importação reconstrói caixa/posições sem duplicatas; empresa pesquisável com documentos auditados e explicação do Mentor; operação registrada não envia ordem; dashboard/performance/relatório concordam; dados e preferências sobrevivem a reinício; backup recuperável; sete skills avaliadas; motores identificados e linha de base efetivamente medida.

## Etapa 2 — Análise avanççada, classes de ativos e estratégias

**Skills (12): S19, S10, S09, S15, S04, S16, S05, S17, S06, S14, S08, S11. Estado: não iniciado.**

1. S19 define pares e contexto; S10, S09 e S15 estabelecem motores brutos próprios de renda fixa, FIIs/dividendos e ETFs/globais. Dependem de identidade, documentos e auditoria da etapa 1.
2. S04 implementa valuation e versões de premissas. S16 verifica normas oficiais e versiona vigência por titular; completa retorno líquido por classe. Nenhuma alíquota do prompt substitui verificação normativa.
3. S05 calcula risco e estresse; S17 fornece o único motor Monte Carlo reutilizado por metas e carteiras. Fixar modelos, janelas, sinal de perdas, RNG e limites antes de acelerar.
4. S06 integra objetivos, custos, liquidez e restrições ao rebalanceamento proposto, com solver e viabilidade explícitos e revalidação após lotes.
5. S14 produz sinais disponíveis no tempo; S08 usa universo histórico, eventos, custos, regras de execução e divisão temporal para evitar look-ahead/sobrevivência/overfitting.
6. S11 combina indicadores canônicos e critérios salvos em candidatos explicáveis, com inclusões, exclusões e qualidade.
7. Integrar cada motor a contrato, serviço, wrapper/skill, MCP, tela, explicação, versão e relatório. Páginas novas P05–P07, P09, P13–P17 ampliam bases existentes; não entregar motores isolados.

**Desempenho:** perfilar preparação, cálculo, canonicalização/solver, cópias, persistência e job completo; usar bibliotecas nativas adequadas antes de Rust/Julia. Adotar somente com correção, benefício e distribuição medidos; documentar também a decisão de manter a base.

**Portão da etapa:** doze skills equivalentes por interface/scripts/MCP; valuation editável e histórico; risco/simulação/otimização sem alterações reais; backtest conhecido sem futuro; tributação individual com vigências; FIIs/renda fixa/ETFs com métricas próprias e lacunas claras; radar explicável e relatórios reproduzíveis. Cada módulo acelerado adotado tem identidade, política numérica, benefício e instalação validados.

## Etapa 3 — Comitê IA, colaboração, monitoramento e operação completa

**Skills (4): S13, S18, S20, S22. Estado: não iniciado.**

1. S13 amplia coleta e interpretação de eventos oficiais e reconcilia direitos, revisões/cancelamentos, posições, proventos e teses sobre a contabilidade já existente.
2. S18 processa notícias/documentos legitimamente obtidos, preserva evidências, deduplica e pode concluir inconclusivo. S20 diferencia anomalia econômica, evento legítimo e erro de dados, com avaliação temporal e falsos positivos.
3. S22 fixa snapshot/data, audita, seleciona especialistas pertinentes, produz análises independentes, executa crítica e verificação determinística, preserva divergências e salva síntese e decisão humana separadas. Advogado do diabo não é uma 24ª skill.
4. Ampliar diário, revisão de teses, comentários, menções internas e conflitos de edição; preservar expectativa original e comparar com o realizado.
5. P18/P20 e demais páginas recebem agenda, alertas e relatórios recorrentes; regras com prévia/teste, destinatários internos, tolerância, silêncio, deduplicação e reativação. Canais externos só após configuração expressa.
6. Completar S21 em todas as análises/formatos, operação supervisionada, catch-up após desligamento, observabilidade, recuperação e restauração em ambiente vazio. Revisar todas as páginas e instalação alvo.

**Desempenho e falhas:** medir interface/coleta/jobs/IA concorrentes; coordenar CPU/threads/memória/chamadas; validar cancelamento, retomada, fallback aprovado e instalação dos motores habilitados. Rede/inferência são medidas separadamente do cálculo local. IA indisponível preserva recursos determinísticos.

**Portão da etapa:** evento → auditoria → ativo → alerta → revisão sem duplicação; Comitê com evidências e crítica verificável; colaboração/versões recuperáveis; agendamentos persistentes; restauração completa testada; 23 skills integradas às 23 páginas; formatos exportados conferidos; desktop/celular revisados; instalação limpa e atualização documentadas, recursos limitados e interface utilizável segundo metas medidas.

## Critério para registrar progresso

Estados oficiais: **não iniciado**, **em implementação**, **pronto para revisão**, **validado**, **bloqueado por dependência externa**. Bloqueio identifica fonte, chave, licença, acesso ou documento exato e o que já funciona. Só a integração atualiza evidência de conclusão após verificar o incremento. Uma dependência externa não paralisa trabalhos independentes.

Uma entrega informa mudança, forma de uso, arquivos/serviços, comandos realmente executados, resultados e pendências concretas. Não inventar testes, modelos simultâneos, medições, SSH funcional ou trabalho em segundo plano. Depois dos portões atendidos, seguir para a próxima dependência, sem repetir verificações sem motivo.

## English summary

The plan preserves exactly three stages: seven foundation skills, twelve advanced analysis skills, and four monitoring/AI committee skills. The first Stage 1 increment is a limited but integrated accounting and web/API foundation. Stage completion requires real services, skills, meaningful tests, traceable outputs and operational evidence. Stages 2 and 3 are not started; accelerated engines are adopted only after measured correctness and practical benefit.
