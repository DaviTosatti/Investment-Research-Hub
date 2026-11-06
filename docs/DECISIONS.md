# Registro de decisões

Atualizado em 05/11/2026. Fonte: Promptx.txt, edição/revisão 04/11/2026, e recorte do primeiro incremento definido pela integração. **Decisão de projeto não é implementação validada.** Estados abaixo distinguem diretriz escolhida, código observado e proposta ainda dependente de evidência. STATUS/HANDOFF mantidos pela integração registram execução, comandos e resultados.

## D01 — Escopo em exatamente três etapas

**Estado: diretriz aprovada pelo usuário.** Fundação/experiência/dados/acompanhamento (S01,S02,S12,S03,S07,S21,S23); análise avançada/classes/estratégias (S19,S10,S09,S15,S04,S16,S05,S17,S06,S14,S08,S11); Comitê/colaboração/monitoramento/operação (S13,S18,S20,S22). São 7+12+4 skills, sem etapa adicional.

Incrementos internos permitem publicar trabalho verificável sem concluir artificialmente a etapa. Preservar 23 páginas/10 áreas e 10 skills profissionais: S03,S04,S05,S06,S07,S08,S11,S12,S16,S22. Diário, alertas e carteira inteligente são recursos; crítico é papel do Comitê. Agentes de engenharia não alteram o catálogo de negócio.

## D02 — Um grupo privado, usuários e titulares distintos

**Estado: diretriz escolhida.** Sem arquitetura SaaS multicliente. Contas individuais identificam autoria; vínculo ao grupo permite visão compartilhada; papéis admin/member/viewer distinguem gestão, colaboração e consulta. Titular econômico, conta e carteira são entidades próprias, não aliases do usuário autenticado.

Alternativa rejeitada: conta compartilhada ou presumir que cada usuário só vê a própria carteira. Consequência: autorização no serviço, inclusive busca por ID/API/MCP; admin gerencia usuários/integrações, sem distribuir segredos. Consolidado não compensa tributos entre amigos, não é fundo nem contribuinte único.

## D03 — Identidade fintech escura própria

**Estado: instrução expressa do usuário.** Azul-marinho/grafite, superfícies discretas, primária ciano, menu lateral agrupado, gráficos legíveis e componentes/tokens comuns; verde/vermelho com sentido financeiro. Acessibilidade por teclado/leitor/contraste/símbolos e revisão em 1440/1024/768/390 px.

Não aplicar `padronizar-dashboards`, Dashboard de Adquirência ou template profissional do usuário. As onze imagens fornecidas e examinadas no chat orientam composição, densidade, navegação e gráficos conforme [VISUAL_REFERENCES](VISUAL_REFERENCES.md). A identidade e os dados são próprios do Hub. Templates de relatórios/apresentações também serão do Hub. pt-BR com suporte/cópia inglesa, moeda inequívoca e unidades/datas claras.

## D04 — Monólito modular e stack principal

**Estado: arquitetura escolhida.** Next.js/React/TypeScript estrito no frontend; Python suportado e compatível, FastAPI/Pydantic/SQLAlchemy/Alembic no backend; PostgreSQL principal. API/frontend/worker podem ser processos separados no mesmo repositório. Arquivos persistentes locais com interface futura para armazenamento de objetos.

Alternativas: microserviços imediatos ou várias stacks de cálculo independentes. Consequência: menor custo operacional, regras centralizadas e migração futura local→híbrida→24h sem reescrever motores. Versões instaladas e gerenciadores devem constar em lockfiles; biblioteca de gráficos e dependências adicionais dependem de compatibilidade/exportação/acessibilidade, não são homologadas apenas por constar no prompt.

## D05 — Primeiro incremento verificável da etapa 1

**Estado: primeiro recorte integrado em validação; etapa incompleta.** Login/sessões e papéis, titulares/contas/carteiras/instrumentos, ledger Decimal balanceado e imutável para deposit/withdrawal/buy/sell/dividend/fee/tax/split, idempotência, preço manual persistido, posições/caixa derivados, custo/mercado separados e CSV básico, ligados à UI/API/PostgreSQL.

Consequência: integração real precede expansão de cobertura. Esse recorte não conclui S01/S12/S21 ou toda a etapa 1, não substitui importação completa, performance, fontes, MCP, relatórios e recuperação. Etapas 2 e 3 não iniciadas; provedores e IA não integrados neste registro.

## D06 — Ledger canônico e política inicial BRL

**Estado: diretriz escolhida; implementação inicial observada, não homologada.** Posições/caixa derivam de eventos, com lançamento balanceado e histórico imutável; correção por estorno/retificação versionada. Evento importado de saldo inicial identifica data/origem/limitação do histórico.

Fonte lida: `packages/engines/src/hub_finance/ledger.py`, método `average-cost-brl/1.0.1`. O código usa custo médio, negociação, Decimal com contexto 50, caixa BRL em centavos half-even, entradas até 8 casas e custo parcial em 16 casas, consumindo resíduo exato na venda final. Isso é política do método inicial, não regra universal/fiscal. Sem venda a descoberto/caixa negativo nessa cobertura.

Consequência: API e persistência devem conservar escalas e balanceamento, controlar ordenação e transação e não confundir atomicidade em memória com durabilidade. A validação registrada em STATUS contém 59 testes de domínio e integração aprovados; a cobertura completa da Etapa 1 permanece pendente. Ver [MODEL_REGISTRY](MODEL_REGISTRY.md).

## D07 — Dinheiro exato; ciência derivada

**Estado: política escolhida.** Dinheiro e tributos usam Decimal/NUMERIC e arredondamento explícito; quantidades/preços/taxas/intermediários têm escalas próprias. Matrizes/séries científicas podem usar float64, com pontos de conversão e tolerâncias por grandeza.

Alternativa rejeitada: armazenar ledger/fisco em float ou arredondar todo intermediário em centavos. Fronteiras nativas usam decimal exato/inteiro escalado, limites/overflow validados. fastmath desativado por padrão e nunca no ledger/fisco. Mudança de precisão/aproximação é política versionada, não otimização invisível.

## D08 — Custo não substitui preço de mercado

**Estado: regra financeira escolhida.** Cotação/avaliação manual informa origem, moeda, instante e versão persistida. Sem preço, quantidade/custo/caixa permanecem conhecidos, mas valor de mercado é indisponível; cobertura parcial não se apresenta como total conhecido.

Consequência: não fabricar patrimônio/retorno, não usar zero ou custo como cotação. Última avaliação mostra idade/método; renda fixa separa curva contratual, mercado, saída e vencimento. Retorno total e proventos em caixa seguem convenção única para evitar dupla contagem.

## D09 — Idempotência econômica e correções rastreáveis

**Estado: contrato escolhido.** Identificador de origem + chave econômica + regra explícita e unicidade transacional devem impedir duplicata sequencial/concorrente/entre arquivos. Mesma idempotency_key com corpo diferente retorna conflito; ambiguidades vão para conciliação.

Alternativa insuficiente: hash do arquivo ou checagem apenas no navegador. Preservar original/mapeamento/importador/decisão; não editar o extrato de origem. Efeitos aceitos e intenção são persistidos atomicamente. Campos source/external/revision/estorno/autoria mantêm rastreabilidade.

## D10 — Proveniência e disponibilidade histórica

**Estado: contrato escolhido.** Fonte/documento/hash, período econômico, observação/preço, publicação, disponibilidade, coleta e revisão têm identidades distintas. Originais, normalizados e derivados são preservados. Retificação não reescreve análise anterior silenciosamente.

Consequência: backtests e análises point-in-time escolhem vintages/available_at_cutoff; disponibilidade desconhecida exige hipótese conservadora. IDs de emissor/instrumento/listagem são estáveis e ticker tem vigência. Fontes oficiais têm documentação/licença/limites verificados e alternativas de comprovação pesquisadas; não presumir direito a tempo real ou contratação.

## D11 — Um motor aprovado por execução; acelerar por evidência

**Estado: arquitetura escolhida; nenhuma extensão adicional homologada.** Python coordena e expõe contrato canônico. NumPy/SciPy/SQL e outras bibliotecas adequadas são avaliadas antes de código próprio. Medir algoritmo/índices/lotes/cache e trabalho total, não apenas loop ou chamada HTTP.

Rust via PyO3/Maturin é primeira linguagem adicional para núcleo próprio relevante, se correção/benefício/distribuição forem demonstrados. Julia/JuMP permanece condicional à vantagem científica real; C/C++ prioritariamente por bindings consolidados. Numba é apenas para funções compatíveis. Não criar runtime/crate para cumprir contagem de linguagens.

Consequência: método, implementação e execução têm versões distintas; fallback só pré-validado/identificado, sem trocar método/solver/precisão ou relaxar limite ocultamente. Buffer/dtype/layout/máscara/ownership, RNG/streams/recursos e instalação alvo fazem parte do contrato. Ver [COMPUTE_ARCHITECTURE](COMPUTE_ARCHITECTURE.md).

## D12 — Jobs duráveis e cancelamento explícito

**Estado: política escolhida; mecanismo concreto a implementar/verificar.** Um mecanismo atende trabalhos longos, com estado/progresso persistidos, timeout, recuperação, lease/heartbeat, retries limitados e falha examinável. PostgreSQL+worker dedicado é opção inicial prevista; scheduler único e outbox quando necessário. Não prometer exactly-once.

Consequência: desconexão não cancela job aceito; cancelamento exige intenção persistida/autorizada. Cancelado não reentra automaticamente. CPU roda no worker, limites jobs/processos/threads/memória são coordenados, efeitos financeiros atômicos. BackgroundTasks ou scheduler da API não substituem fila durável. Isolamento de processo atende limite rígido quando biblioteca não cancela com segurança.

## D13 — HTTP e MCP usam os mesmos serviços

**Estado: contratos planejados, sem MCP integrado declarado.** HTTP sob /api/v1 com OpenAPI, validação/paginação/ordem estável, idempotência e conflitos de edição version/ETag. MCP remoto usa Streamable HTTP, SDK oficial fixado e OAuth/OIDC compatível, validando emissor/assinatura ou introspecção/expiração/audiência/recurso/escopos.

Identidade da pessoa vem de sujeito+emissor, não client_id. Anotações read-only não substituem autorização; análise pode criar job/relatório sem alterar ledger. Recursos de job/artefato precisam ser acessíveis/autorizados; caminho local/localhost não é integração remota comprovada. Site privado, SSH/Tailscale e MCP são acessos distintos. Não expor execução arbitrária de SQL/código/shell.

## D14 — IA como interpretação e crítica com evidências

**Estado: requisito futuro, sem provedor de IA integrado na aplicação.** Adaptador por tarefa e modelos/SDK/API realmente disponíveis; preferência Astra/Sol não implica integração automática nem prova dois modelos usados no desenvolvimento. Registrar modelo/esforço observados; validar parâmetros no catálogo atual.

Documentos são dados, não instruções. IA recebe resultados canônicos e evidências, com orçamento/tempo/chamadas/concorrência. Comitê produz análises independentes, crítico, validação determinística e divergências, podendo ser inconclusivo; votação não cria porcentagem de confiança e fontes repetidas não são independentes. Falha de IA preserva recursos determinísticos. Não contratar, publicar acesso, enviar mensagens ou executar transações por inferência.

## D15 — Colaboração, alertas e fusos

**Estado: requisitos escolhidos, cobertura inicial e futura conforme plano.** Diário/teses conservam original e revisões com autoria/justificativa; edição concorrente não sobrescreve silenciosamente. Comentários/menções e alertas internos respeitam grupo.

Regras de alerta têm escopo/fonte/condição/tolerância/frequência/destinatários/silêncio/dedup/reativação e prévia/teste. E-mail/Telegram/Discord só enviam após configuração expressa; Outlook não é dependência presumida. Apresentação/agendamento em America/Sao_Paulo, timestamps com timezone e calendário da bolsa. Operação local depende da máquina ligada; catch-up evita avalanche de alertas antigos.

## D16 — Instalação, saúde e recuperação comprováveis

**Estado: política escolhida; procedimentos executáveis/testados dependem da integração.** Validar um caminho principal no ambiente real: Linux/WSL2+Compose quando disponível ou nativo já suportado; não exigir todos simultaneamente. Não afirmar SSH ao computador pessoal sem conexão efetivamente testada. Serviços supervisionados, dados fora de temporários e atualização por migrações.

Logs sem segredos/extratos, saúde de processo/banco/provedor/atualidade/motor separadas. Backup abrange geração coerente de PostgreSQL, originais, snapshots, relatórios e configuração, com hashes/schema; credenciais separadas. Retenção/destino/periodicidade seguem uso real. Só restauração em destino vazio com referências válidas comprova recuperação; sincronização de pasta não basta.

## D17 — Conclusão depende de evidência, não de inventário

**Estado: regra de entrega escolhida.** Matriz usa não iniciado/em implementação/pronto para revisão/validado/bloqueado por dependência externa. Skill completa exige contrato/cálculo/serviço/MCP quando aplicável/UI/skill-wrapper/evals/fontes-versões/exportação-histórico/operação; cálculo intensivo também exige linha de base e escolha fundamentada.

Consequência: documentação, biblioteca instalada, tela estática, mock, crate compilado ou teste de texto decorativo não concluem recurso financeiro. Metas vêm depois de medir; não há ganho ou benchmark inventado. A integração faz commit/push Conventional Commits por incremento verificado e mantém STATUS/HANDOFF. Segredos, carteiras reais, extratos, caches e backups ficam fora do Git; revisar conteúdo antes de publicar.

## English summary

These decisions preserve the user's full three-stage scope, one private group, separate economic ownership and individual authorship, a proprietary dark fintech design, modular monolith services and exact accounting. The initial ledger source is recorded without certifying complete integration. External providers, MCP, AI and native acceleration remain unverified/planned. Completion requires real functionality, tests, traceability and recovery evidence; the integrator owns commits and publication.


## D18 — Limites explícitos do primeiro recorte

BRL, eventos append-only em ordem cronológica por carteira e consulta limitada a
20 mil eventos. O limite é verificado antes de aceitar mais registros para que a
carteira continue consultável. Correções históricas, importação e jobs são próximos
blocos da Etapa 1, não funcionalidades removidas. Paginação cobre listas na API.

A soma de custos e o bruto usam contexto Decimal de precisão 50; JSON monetário
recebe strings e devolve strings. A API usa o bruto do motor, evitando outra fórmula.
Snapshot de consulta é um hash das identidades/versões selecionadas; CSV com
`snapshot_id` rejeita alteração concorrente. Histórico usa revisões hoje conhecidas;
consulta point-in-time e persistência de análises são requisitos ainda pendentes.
Avaliação do mesmo dia, cadastrada antes de um split, não avalia a posição alterada.

## D19 — Entrega pelo GitHub e verificação visual

Código entregue em branch de trabalho com commits e push por incremento;
PR #1 em rascunho para revisão. A solicitação atual é desenvolvimento no repositório,
sem implantação compartilhada da plataforma. Build não equivale a teste no navegador.
O ambiente managed-linux não disponibilizou `cua_repl.js`; revisão visual/E2E fica
pendente conforme a regra da skill Sites para essa ausência. Não foi iniciado
servidor de preview nem declarado um teste visual que não ocorreu.
