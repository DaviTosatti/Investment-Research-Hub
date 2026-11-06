# Contrato do primeiro incremento — Etapa 1

Contrato de integração em implementação; não representa a conclusão da Etapa 1.
API em `/api/v1`, valores decimais como strings JSON, datas ISO 8601, moeda BRL
neste incremento. IDs UUID; nomes de usuário não representam a titularidade econômica.

## Acesso

- `POST /auth/login` `{email,password}` → `{user}`; cookie HttpOnly `hub_session`.
- `GET /auth/session` → `{user}`; `POST /auth/logout` → 204.
- Toda escrita inclui `X-Hub-Request: 1`. Sem CORS; origem validada no servidor.
- `user`: `{id,name,email,role}`; roles `admin`, `member`, `viewer`.
- Admin cria usuários; admin/member registram dados; viewer consulta os dados do grupo.
- `GET /members` → lista paginada; `POST /members` `{name,email,password,role}`.

Listas abaixo retornam `{items,total,limit,offset}` (padrão 100, máximo 200).
Erros retornam `{error:{code,message}}`, inclusive validação 422, sem dados sensíveis.

## Cadastros

- `GET/POST /owners`; criação `{name}`; item `{id,name}`.
- `GET/POST /portfolios`; criação `{name,owner_id,account_name,currency:"BRL"}`;
  item `{id,name,owner_id,owner_name,account_name,currency,created_at}`.
- `GET/POST /instruments`; criação `{ticker,name,asset_class,currency:"BRL",exchange:"B3"}`;
  item inclui `id`. Classes `stock`, `fii`, `etf`, `fixed_income`, `other`.
  Identidade estável por ID; ticker identifica uma listagem, não substitui o ID.
- `POST /prices` `{instrument_id,price,as_of,source}`; avaliação manual versionada,
  `price` decimal positivo, `as_of` data, `source` descrição não vazia.

## Operações realizadas

`POST /transactions` recebe `{portfolio_id,instrument_id?,event_type,quantity?,unit_price?,
gross_amount?,fees:"0",taxes:"0",trade_date,settlement_date?,source:"manual",external_id?,
idempotency_key,notes?}`. Decimal sempre string, ponto decimal, até 8 casas nos inputs.

Tipos deste incremento: `deposit`, `withdrawal`, `buy`, `sell`, `dividend`, `fee`, `tax`,
`split`. Compra/venda: quantity e unit_price positivos; gross_amount derivado.
Aporte/retirada/dividendo/taxa/imposto: gross_amount positivo. Split: quantity é o
fator positivo, conserva custo, não movimenta caixa. Não aceita short nem caixa negativo.
Eventos futuros são rejeitados. Não envia ordens a corretoras.

Item de saída: `{id,portfolio_id,portfolio_name,owner_name,instrument_id,ticker,event_type,
quantity,unit_price,gross_amount,fees,taxes,trade_date,settlement_date,source,external_id,
notes,created_by,created_at,revision}`. `GET /transactions` aceita portfolio_id,
owner_id, as_of, limit, offset. Chave repetida com mesmo corpo reutiliza o evento;
com corpo diferente retorna 409. Histórico e lançamentos são append-only neste incremento.

## Painel e consultas

`GET /dashboard?portfolio_id=&owner_id=&as_of=YYYY-MM-DD` retorna:

```ts
type Dashboard = {
  as_of: string; currency: 'BRL'; generated_at: string;
  summary: {
    cash: string; net_contributions: string; income: string; realized_pnl: string;
    total_cost: string; equity_at_cost: string; market_value: string | null;
    equity: string | null; unrealized_pnl: string | null;
    performance: null; performance_reason: string;
  };
  positions: Array<{
    portfolio_id: string; portfolio_name: string; owner_name: string;
    instrument_id: string; ticker: string; name: string; asset_class: string;
    quantity: string; cost_basis: string; average_cost: string;
    last_price: string | null; price_as_of: string | null; price_source: string | null;
    market_value: string | null; unrealized_pnl: string | null;
    quality: 'valid' | 'stale' | 'unavailable';
  }>;
  history: Array<{date: string; net_contributions: string; equity_at_cost: string}>;
  allocation: Array<{asset_class: string; cost_basis: string; weight: string}>;
  activity: Array<{id: string; event_type: string; ticker: string | null;
    portfolio_name: string; owner_name: string; gross_amount: string; trade_date: string}>;
  warnings: string[]; method_version: string;
};
```

Custo não é valor de mercado. Ausência de cotação produz null e mensagem;
última avaliação manual com mais de 7 dias fica desatualizada, com referência visível.
Histórico é posição a custo, não rentabilidade. TWR/MWR ficam pendentes de séries e fluxos
suficientes. Taxas e tributos registrados não constituem apuração fiscal (Etapa 2).

`GET /reports/positions.csv` usa os mesmos filtros e motor do painel. O parâmetro
`snapshot_id`, retornado pelo painel, rejeita com 409 uma exportação se os dados
mudaram desde a consulta, evitando divergência silenciosa.
`GET /audit` (lista paginada) → `{id,action,entity_type,entity_id,actor_name,created_at}`.
`GET /health` → estado do banco, versão da aplicação; sem segredos.

Limites atuais: eventos em ordem cronológica por carteira, até 20 mil eventos
por consulta/carteira; limites são verificados antes da gravação. Caixa usa
data de negociação, sem alegar saldo liquidado. Decimais enviados como números
JSON são rejeitados para evitar conversão implícita em ponto flutuante.
Eventos no mesmo dia seguem a sequência de registro; horários de execução e
conciliação intradiária completa serão acrescentados com a importação.
Consulta histórica reconstrói a data econômica com as revisões hoje conhecidas;
não constitui consulta point-in-time para backtesting. Correções de eventos,
imports e snapshots de análises persistidos permanecem no plano da Etapa 1.

## English summary

First Stage 1 slice: cookie sessions, shared-group authorization, separate economic owners,
BRL portfolios, instruments, exact immutable event ledger, manual price snapshots, derived
dashboard and filtered CSV. All figures come from the Python engine. Missing quotes remain
null; cost history is explicitly distinct from investment performance. Later stages remain
in the implementation plan, not in the first-slice completion claim.
