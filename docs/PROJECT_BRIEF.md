# Investment Research Hub — visão do projeto

Atualizado em 05/11/2026. Fonte de escopo: Promptx.txt, edição e revisão técnica de 04/11/2026, lido integralmente. Este documento registra requisitos e decisões; não comprova implementação.

## Objetivo e público

Plataforma web privada para um único grupo de amigos de confiança aprender, pesquisar, analisar, registrar investimentos já realizados e acompanhar decisões. Os objetivos permanentes são **entender**, **analisar e decidir** e **monitorar**. O ciclo completo é pesquisa → riscos → preço → tese → simulação na carteira → registro da operação realizada → acompanhamento.

O acesso compartilhado não elimina titularidade: usuário autenticado é autor de ações; titular econômico é proprietário de patrimônio e sujeito da apuração fiscal. Contas, carteiras, operações, documentos e resultados conservam essa distinção. O consolidado é uma visão analítica, não fundo, conta conjunta ou contribuinte único. Não haverá SaaS multicliente, assinaturas, promessa de ganhos ou envio de ordens a corretoras neste escopo.

## Compromisso de entrega

Há exatamente **três etapas**, com **23 skills**, **23 páginas/subpáginas**, **10 áreas de navegação** e **10 skills do núcleo profissional**. Incrementos são entregas internas dessas etapas; não são novas etapas nem reduzem o compromisso final.

| Etapa | Skills, na ordem de dependência do prompt | Propósito |
| --- | --- | --- |
| 1 | S01, S02, S12, S03, S07, S21, S23 | Fundação, experiência visual, dados e acompanhamento |
| 2 | S19, S10, S09, S15, S04, S16, S05, S17, S06, S14, S08, S11 | Análise avançada, classes de ativos e estratégias |
| 3 | S13, S18, S20, S22 | Comitê IA, colaboração, monitoramento e operação completa |

Núcleo profissional: S03, S04, S05, S06, S07, S08, S11, S12, S16 e S22. Diário, alertas e carteira inteligente são recursos; advogado do diabo é papel do Comitê. Agentes de desenvolvimento não são skills adicionais de negócio.

## Primeiro incremento da etapa 1

Escopo definido para a integração: frontend Next.js/React/TypeScript estrito, identidade fintech escura; backend FastAPI/Pydantic/SQLAlchemy/Alembic e PostgreSQL; login e sessões individuais com admin/member/viewer para o grupo; titulares separados de usuários; carteiras, contas e instrumentos; ledger imutável, balanceado e Decimal para aporte, retirada, compra, venda, dividendo, taxa, imposto e split; idempotência; preços manuais persistidos; caixa e posições derivados; custo separado de mercado; ausência de cotação indicada como indisponibilidade; exportação CSV básica e validações significativas.

Esse incremento é uma cobertura parcial da fundação. Não conclui S01, S12, S21 nem a etapa 1. Importação CSV/XLSX completa, performance financeira, fontes externas, demais eventos, motores, skills executáveis, MCP e recuperação continuam no compromisso da etapa 1. Não há integração de provedores ou IA validada neste registro. Etapas 2 e 3 não foram iniciadas.

## Regras permanentes

- Dados financeiros e operações persistem no servidor; cache do navegador não é fonte contábil. Posições e caixa são reconstruídos de eventos; correções deixam estorno ou revisão rastreável.
- Dinheiro e tributos usam Decimal/NUMERIC, escalas e arredondamento explícitos. Ausência não vira zero. Valor de custo não substitui preço de mercado. Preço, retorno total, renda e fluxo externo têm naturezas distintas.
- Fontes, unidades, datas econômicas, divulgação, disponibilidade histórica e revisões são preservadas. Cada análise identifica snapshot, método, implementação, parâmetros e limitações.
- Uma implementação aprovada por motor atende interface, HTTP, wrappers, MCP e relatórios. IA explica e critica resultados; não cria fórmulas financeiras concorrentes.
- Autorização é aplicada nos serviços. Membros autorizados veem os dados comuns; externos não acessam por conhecer um ID. Credenciais técnicas ficam restritas.
- Simulações não alteram carteiras reais. Tributos são individuais e versionados; o sistema não transmite declarações nem efetua pagamentos.
- Jobs longos são persistentes, com progresso, recuperação e cancelamento explícito. Falha de uma fonte ou da IA preserva funções independentes.
- Código, documentação e fixtures públicas ou sintéticas permitidas entram no Git. Carteiras reais, extratos, segredos, caches e backups ficam fora; revisar documentos antes de cada commit.

## Identidade e experiência

As onze imagens fornecidas e confirmadas pelo usuário em 05/11/2026 foram
examinadas; sua aplicação por tela/etapa está em
[VISUAL_REFERENCES.md](VISUAL_REFERENCES.md). FinSight/Stockly orientam a
composição principal, Chainx a navegação e as referências técnicas as análises.

Design próprio em azul-marinho/grafite, superfícies discretas, primária azul-ciano, números tabulares, gráficos legíveis e menu lateral agrupado. Verde/vermelho expressam significado financeiro; séries também usam rótulos, símbolos e traços. A skill pessoal **padronizar-dashboards**, o Dashboard de Adquirência e integrações profissionais como Outlook não se aplicam.

Usar português brasileiro e suporte a inglês, moedas inequívocas, datas dd/mm/aaaa e fuso padrão de apresentação/agendamento America/Sao_Paulo; timestamps canônicos com timezone. Revisar teclado, foco, leitores de tela, contraste, movimento reduzido e larguras 1440/1024/768/390 px com capturas reais. Toda página informa carregamento, vazio, erro, dados parciais, antigos e normais.

Um único contexto de titular/carteira/grupo, período, moeda e versão governa cartões, gráficos, tabelas e exportações. Respostas atrasadas não substituem uma seleção posterior. A linha do tempo depende do período, não do documento aberto. Consolidação usa datas compatíveis e fluxos reais, sem média simples de rentabilidades.

## Execução e evidência

O integrador mantém código, commits Conventional Commits e push de cada incremento verificado. Esta frente altera somente os oito documentos designados; não faz commit ou push. Preferências Astra/Sol e esforço elevado dependem da disponibilidade real: registrar modelo/esforço observados, sem atribuir execução a modelos não utilizados.

Conclusão exige requisito rastreado, contrato, implementação, serviço/tela e MCP quando aplicável, skill e wrapper funcionais, testes executados, origem e versões, exportação/histórico e operação documentada. A arquitetura híbrida exige correção e medição; Rust e Julia entram apenas com benefício demonstrado. Consultar [plano](IMPLEMENTATION_PLAN.md), [matriz](REQUIREMENTS_MATRIX.md) e registros de STATUS/HANDOFF mantidos pela integração para evidência atual.

## English summary

Investment Research Hub is a private platform for one trusted group, covering learning, research, portfolio accounting and decision monitoring. Its scope remains exactly three stages, 23 business skills and 23 pages in 10 navigation areas. Users and economic owners are separate. The initial Stage 1 increment establishes the web/API foundation and exact, immutable accounting; no complete skill, external provider, AI integration or later stage is certified here. A proprietary dark fintech design replaces the user's unrelated dashboard template.
