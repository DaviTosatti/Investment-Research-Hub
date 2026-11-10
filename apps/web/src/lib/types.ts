export type Role = "admin" | "member" | "viewer";
export type User = { id: string; name: string; email: string; role: Role };
export type PageResult<T> = { items: T[]; total: number; limit: number; offset: number };
export type Owner = { id: string; name: string };
export type Portfolio = { id: string; name: string; owner_id: string; owner_name: string; account_name: string; currency: "BRL"; created_at: string };
export type AssetClass = "stock" | "fii" | "etf" | "fixed_income" | "other";
export type Instrument = { id: string; ticker: string; name: string; asset_class: AssetClass; currency: "BRL"; exchange: string };
export type EventType = "deposit" | "withdrawal" | "buy" | "sell" | "dividend" | "fee" | "tax" | "split";
export type Transaction = {
  id: string; portfolio_id: string; portfolio_name: string; owner_name: string;
  instrument_id: string | null; ticker: string | null; event_type: EventType;
  quantity: string | null; unit_price: string | null; gross_amount: string;
  fees: string; taxes: string; trade_date: string; settlement_date: string | null;
  source: string; external_id: string | null; notes: string | null;
  created_by: string; created_at: string; revision: number;
};
export type Position = {
  portfolio_id: string; portfolio_name: string; owner_name: string;
  instrument_id: string; ticker: string; name: string; asset_class: string;
  quantity: string; cost_basis: string; average_cost: string;
  last_price: string | null; price_as_of: string | null; price_source: string | null;
  market_value: string | null; unrealized_pnl: string | null;
  quality: "valid" | "stale" | "unavailable";
};
export type Dashboard = {
  as_of: string; currency: "BRL"; generated_at: string; snapshot_id: string;
  summary: {
    cash: string; net_contributions: string; income: string; realized_pnl: string; expenses: string;
    total_cost: string; equity_at_cost: string; market_value: string | null;
    equity: string | null; unrealized_pnl: string | null;
    performance: null; performance_reason: string;
  };
  positions: Position[];
  history: { date: string; net_contributions: string; equity_at_cost: string }[];
  allocation: { asset_class: string; cost_basis: string; weight: string }[];
  activity: { id: string; event_type: EventType; ticker: string | null; portfolio_name: string; owner_name: string; gross_amount: string; trade_date: string }[];
  warnings: string[]; method_version: string;
};
export type AuditEntry = { id: string; action: string; entity_type: string; entity_id: string; actor_name: string; created_at: string };
export type Filters = { owner_id: string; portfolio_id: string; as_of: string };
