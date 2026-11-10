# Frontend — primeiro incremento da Etapa 1

Interface Next.js em pt-BR e inglês para as APIs existentes: sessão e papéis,
painel filtrado por titular/carteira/data, cadastros, eventos realizados,
avaliações manuais, auditoria e participantes. A identidade é fintech navy,
própria deste projeto. Este incremento não conclui a Etapa 1.

Com a API disponível em `127.0.0.1:8000`, instale com `npm ci` e execute
`npm run dev`. O rewrite de `/api/v1` usa `HUB_API_URL` quando configurado
(consulte `.env.example`). Sessões usam cookie; toda mutação inclui
`X-Hub-Request: 1`.

Valores financeiros são enviados como strings. Os campos aceitam vírgula ou
ponto decimal, sem agrupamento de milhares, com até oito casas. O motor Python
calcula posições, caixa, resultados, histórico e alocação. O frontend apenas
formata esses resultados e os representa em gráficos.

Preços unitários, cotações e custo médio exibem até oito casas decimais;
valores de caixa e totais são apresentados em centavos. Horários usam
`America/Sao_Paulo`; datas de referência sem horário conservam o dia informado.

O painel usa quatro cartões compactos, histórico em área/linha à esquerda,
donut de alocação à direita e tabela de posições em toda a largura. O donut
representa apenas os pesos recebidos do motor, sem renormalização. As cores
por classe são estáveis entre filtros; a legenda em tabela preserva custo e
percentual acessíveis. Navegação, filtros e ações mantêm as integrações reais.

O caixa é reconhecido na negociação; liquidação é informativa. Histórico a
custo e patrimônio a mercado têm identificações distintas. Ausência de avaliação,
avaliação anterior a desdobramento e preços desatualizados mantêm os avisos
do servidor. O CSV envia os filtros e `snapshot_id` da consulta exibida;
um conflito 409 exige atualização explícita antes de nova exportação.

Verificações locais:

```sh
npm test
npm run typecheck
npm run lint
NEXT_TELEMETRY_DISABLED=1 npm run build
```

Os testes cobrem representação decimal, retries com idempotência, cabeçalhos e
cookies, paginação completa, respostas canceladas, consistência do CSV,
sessões, formatação, data de negócio e renderização acessível dos gráficos.
São testes unitários do cliente;
não demonstram a jornada completa em navegador com banco real.

Limite de validação nesta retomada: `SITES_MANAGED_LINUX_CONTAINER=1` e
`cua_repl.js` indisponível. QA visual e jornada no navegador ficam pendentes,
conforme a regra informada da skill Sites: “If cua_repl.js is unavailable,
skip browser QA”. Nenhum servidor de preview ou navegador alternativo foi iniciado.

English: this is the first Stage 1 frontend slice, with existing API integration
and unit/build checks. Visual and browser-based end-to-end QA remain pending.
