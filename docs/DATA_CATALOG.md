# Catálogo de dados, fontes e qualidade

Atualizado em 05/11/2026. Fonte: Promptx.txt §§5–6,8–9,11. **Não há provedor externo integrado ou validado neste catálogo.** URLs são referências da especificação, ainda sujeitas a verificação atual de documentação, acesso, termos e cobertura. Avaliações manuais e operações têm persistência e testes PostgreSQL no primeiro incremento; importação de arquivos ainda está planejada.

## Camadas e contratos

1. **Original:** arquivo/payload imutável, hash, fonte, data de coleta e termos aplicáveis. Revisão cria nova versão. Nunca modificar o extrato original; usar cópia local para arquivos em rede.
2. **Normalizada:** identidades, datas, unidades, moedas e escopo explícitos; mantém vínculo com cada original e regra/versão de transformação. Rejeições e escolhas de conciliação são registradas.
3. **Derivada:** posições, retorno, indicadores, cenários e relatórios canônicos; vinculados a snapshots e manifesto de execução. Custo não é substituto de cotação; browser não é repositório oficial.

Entidades necessárias: usuários/vínculo ao grupo, titulares econômicos, contas/carteiras, emissores/instrumentos/listagens, moedas/calendários/preços, documentos/fatos contábeis, macro/eventos, operações/lançamentos/posições/proventos, regras fiscais, snapshots/análises/premissas/relatórios, teses/comentários/revisões, alertas/jobs/auditoria. Um ticker é alias com intervalo de validade; IDs internos são estáveis. Não confundir emissor, classe, instrumento e bolsa/listagem.

### Envelope mínimo previsto

| Dimensão | Campos | Regra |
| --- | --- | --- |
| Identidade | `record_id`, `instrument_id`, `issuer_id` | Aplicar IDs pertinentes; resolver listagem/classe/bolsa sem duplicar ativo ou capitalização. |
| Origem | `source_id`, `source_document_id`, `source_url`, `raw_payload_hash` | Origem rastreável; URL não substitui cópia/versionamento quando permitido. |
| Tempo econômico | `reference_period_start`, `reference_period_end`, `observed_at`/`market_timestamp` | Separar estoque, fluxo e instante de preço. |
| Conhecimento/coleta | `published_at`, `available_at`, `retrieved_at` | Divulgação não é coleta. Cutoff histórico usa disponibilidade; se desconhecida, hipótese conservadora e flag. |
| Versão | `source_version`, `revision_id`, `snapshot_id` | Retificação não sobrescreve histórico. Seleção antiga versus atual é explícita. |
| Grandeza | `currency`, `unit`, `scale`, `consolidation_scope` | Reais/milhares/milhões, ações/cotas, consolidado/individual e frequência não são intercambiáveis. |
| Qualidade | `quality_status`, `quality_flags`, motivo de ausência | Ausência não vira zero nem preço artificial. Não aplicável é distinguido de não disponível. |

Timestamps canônicos têm timezone; apresentação/agendamento usam America/Sao_Paulo por padrão. O calendário da bolsa governa negociação, não o fuso da máquina. Dados anuais/trimestrais/mensais/diários seguem regras de atualidade próprias; um dado antigo pode ser correto para análise histórica.

## Inventário inicial de fontes

Todos os registros externos estão **planejados / documentação e direitos não verificados nesta sessão**. Atraso/frequência devem ser confirmados por objeto e contrato; não são promessas de tempo real. Uma chave ausente só passa a bloqueio depois de identificar a dependência efetiva.

| ID | Fonte e objeto | Cobertura, calendário e unidade a validar | Acesso, direitos e histórico | Situação / dependência |
| --- | --- | --- | --- | --- |
| MANUAL-PRICES | Avaliações/cotações informadas por membro | Instrumento/listagem, preço positivo Decimal, moeda, instante e método/origem informados | Autoria e histórico de revisões; não rotular como feed de mercado. Persistir snapshot manual separado de custo. | Persistido e testado no primeiro incremento; versões append-only, fonte, data, autoria e hash. Sem feed externo. |
| MANUAL-IMPORT | CSV/XLSX de operações e saldos iniciais | Conta/titular/carteira, encoding/separador/número/data/moeda, origem/ID econômico | Original preservado, mapeamento e versão do importador, consentimento e armazenamento privado | Importador completo previsto na etapa 1; exportação CSV básica não é importação. |
| SYNTHETIC | Fixtures e demonstração explicitamente sintéticas | Cenários pequenos conhecidos e cargas de crescimento; sem dados pessoais | Identificar seed/gerador e licença dos elementos públicos, quando usados; separar de carteiras reais | Permitido para testes/demonstração; não comprova integração. |
| CVM-DFP | [CVM DFP](https://dados.cvm.gov.br/dataset/cia_aberta-doc-dfp) | Demonstrações anuais brasileiras, escopos/contas/moedas/escalas/datas | Verificar distribuição, termos e versões; conservar reapresentações e documento | Planejado, etapa 1 / S03,S12. |
| CVM-ITR | [CVM ITR](https://dados.cvm.gov.br/dataset/cia_aberta-doc-itr) | Intermediárias; distinguir acumulado versus isolado e saldos versus fluxos | Preservar períodos/revisões e divulgação; não inferir conhecimento histórico pela coleta | Planejado, etapa 1 / S03,S12. |
| BCB-SGS | [Banco Central SGS](https://dadosabertos.bcb.gov.br/dataset/432-taxa-de-juros---meta-selic-definida-pelo-copom) | Séries de juros/câmbio/atividade; Selic meta não é taxa efetiva | Confirmar código, unidade, frequência e limites atuais; paginar por períodos quando requerido | Planejado, etapa 1 / S07,S02. |
| IBGE | Indicadores oficiais do IBGE | Inflação, atividade e emprego por competência/frequência/território | Consultar documentação oficial antes de criar endpoints; preservar divulgação/revisões | Planejado, etapa 1 / S07. |
| B3-LICENSED | B3 e fornecedores licenciados | Preço/OHLCV/volume/índices/eventos/calendário/listagens, conforme produto contratado | Verificar acesso, atraso, ajustes, uso/exibição e histórico/deslistados; não presumir gratuidade ou direitos de tempo real | Planejado; não autoriza contratação. |
| ISSUER-OFFICIAL | RI de empresas, fundos, administradores e emissores | Comunicados, informes, proventos, emissões, holdings, vacância/crédito e características de títulos | Verificar documento oficial, data/cancelamento e direito de obtenção; não depender só de scraping instável | Pesquisa básica 1; classes 2; monitoramento S13 em 3. |
| SEC-EDGAR | [SEC EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) | Filings/fatos de emissores estrangeiros; conceitos, moeda e exercícios | Confirmar políticas de acesso/identificação/limites, taxonomias e emendas | Planejado / fundamentos globais; cobertura não presumida. |
| FRED-ALFRED | [FRED/ALFRED real-time periods](https://fred.stlouisfed.org/docs/api/fred/realtime_period.html) | Séries macro e vintages disponíveis | Confirmar autenticação/limites e direitos por série; conservar disponibilidade histórica, não usar versão atual como passada | Planejado, etapa 1 / S07. |
| GLOBAL-MARKET | Provedor adequado a preços e fundos internacionais, ainda a selecionar | Bolsa/moeda/calendário/ajustes/ETFs/deslistados | Comparar cobertura, licença, atraso e versões; validar equivalência com fonte alternativa | Planejado; nenhuma seleção/contratação concluída. |
| CURVES-CALENDARS-FX | Fontes oficiais/licenciadas apropriadas ao instrumento | Curvas, indexadores, feriados/dias úteis, câmbio e convenção de cotação | IDs e versões da curva/calendário, defasagem/indexação, timestamp e critérios da conversão | Etapa 1 no recorte necessário; classes completas 2. |
| ETF-HOLDINGS | Emissor/administrador ou fornecedor autorizado | Composição com data, peso, instrumento/listagem, domicílio e benchmark | Marcar holdings parciais/desatualizadas e fundos aninhados; verificar redistribuição | Planejado, etapa 2 / S15. |
| TAX-OFFICIAL | [Receita: compensações](https://www.gov.br/receitafederal/pt-br/assuntos/meu-imposto-de-renda/pagamento/renda-variavel/bolsa-de-valores-1/compensacoes), [IRPF por exercício](https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/dirpf) e atos normativos | Jurisdição/residência/categoria/operação/vigência e competência; ano do fato versus exercício | Revisar norma na implementação e atualização. Manter fonte oficial, coleta, versão e revisão; não copiar alíquotas do prompt | Planejado, etapa 2 / S16; nenhuma regra fiscal homologada. |
| NEWS-TEXT | Notícias, comunicados e transcrições obtidos legitimamente | Publicação original/republicação, autoria, entidades, idioma, corte temporal | Licença e retenção por fonte; texto externo é dado, não instrução; não replicar conteúdo protegido além do permitido | Planejado, etapa 3 / S18,S22. |

Para cada adaptação, completar antes da homologação: documentação verificada/data, contato/URL oficial, objetos cobertos, unidade/moeda/calendário, frequência/atraso, limites/timeouts/retries, autenticação necessária sem valor secreto, direitos de uso/armazenamento/exportação, extensão histórica/vintages, ajustes, prioridade, versão do adaptador e testes. Fontes principais devem ter alternativas pesquisadas para comprovação; mais fontes não significam independência quando replicam a mesma origem.

## Validação, conciliação e disponibilidade

| Estado de qualidade | Uso e apresentação |
| --- | --- |
| válido | Passou pelas regras aplicáveis ao uso/data; não implica garantia universal de precisão. |
| incompleto | Cobertura insuficiente; métricas independentes podem funcionar, resultado informa parcialidade. |
| desatualizado | Exibir último dado válido, idade e referência; não confirmar gatilho com cotação antiga. |
| divergente | Preservar fontes e critérios de prioridade/equivalência; requer conciliação, sem mistura silenciosa. |
| em quarentena | Não liberar para cálculo dependente até resolver regra impeditiva; original permanece recuperável. |
| indisponível | Valor null e motivo estruturado; não substituir por zero, custo ou estimativa não identificada. |

Validar schema, identidade, datas, duplicatas, escalas, totais, consistência contábil e reconciliação de posições/eventos. Tolerâncias são por grandeza e método. Comparar preço de mesma listagem/data/moeda/convenção de ajuste e calendários compatíveis. Preservar escolha autorizada e impacto nas análises. Reimportação usa origem/identificador econômico e decisão rastreável; hash de arquivo sozinho não impede duplicata entre arquivos distintos.

Uma posição sem preço continua com quantidade/custo/caixa conhecidos e **mercado indisponível**. Se apenas parte da carteira tem preços, o consolidado informa cobertura/partial e não apresenta soma incompleta como patrimônio total. Renda fixa distingue valor pela curva, mercado, estimativa de saída e projeção de vencimento. Proventos anunciados, cancelados, projetados e recebidos têm status/efeitos diferentes; série ajustada e caixa não duplicam retorno.

## Preservação, privacidade e recuperação

Dados financeiros são privados ao grupo, com titularidade e autoria preservadas. Extratos, posições reais, anexos pessoais, backups, caches e segredos não entram no Git, nem em exemplos/logs. Fixtures permitidas têm identificação clara. Arquivos ficam em armazenamento persistente com interface futura para objetos, referências/hashes e acesso autorizado; caminho local de servidor não é link para participante remoto.

Retenção/destino/periodicidade de backup serão definidos conforme uso real; não há política executada declarada aqui. Backup deve conservar geração coerente de PostgreSQL, originais, snapshots e relatórios, com hashes/schema; credenciais são separadas. Restauração em ambiente vazio valida referências e arquivos, não apenas existência de um arquivo de backup.

## English summary

No external provider is integrated or certified by this catalog. It defines planned official/manual/synthetic sources, provenance and historical availability, three storage layers, quality states, reconciliation and licensing checks. Missing prices remain unavailable; cost is never substituted for market value. Private financial data, raw personal files and backups stay out of Git, and recovery requires a coherent database/artifact restore.
