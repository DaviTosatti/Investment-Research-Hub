export const decimalPattern = "[0-9]+([.,][0-9]{1,8})?";
export const text = (data: FormData, name: string) => String(data.get(name) ?? "").trim();
export class DecimalInputError extends Error {
  constructor() { super("invalid_decimal"); this.name = "DecimalInputError"; }
}
export function decimal(data: FormData, name: string): string {
  const value = text(data, name);
  // Grouping separators and exponent notation are deliberately rejected as ambiguous inputs.
  if (value && !new RegExp(`^(?:${decimalPattern})$`).test(value)) throw new DecimalInputError();
  return value.replace(",", ".");
}

// Only normalize representation. Amounts, balances and P&L are calculated by Python.
export function transactionPayload(data: FormData) {
  const eventType = text(data, "event_type");
  const trade = eventType === "buy" || eventType === "sell";
  return {
    portfolio_id: text(data, "portfolio_id"),
    event_type: eventType,
    ...(text(data, "instrument_id") ? { instrument_id: text(data, "instrument_id") } : {}),
    ...(trade || eventType === "split" ? { quantity: decimal(data, "quantity") } : {}),
    ...(trade ? { unit_price: decimal(data, "unit_price") } : {}),
    ...(!trade && eventType !== "split" ? { gross_amount: decimal(data, "gross_amount") } : {}),
    fees: decimal(data, "fees") || "0", taxes: decimal(data, "taxes") || "0",
    trade_date: text(data, "trade_date"),
    ...(text(data, "settlement_date") ? { settlement_date: text(data, "settlement_date") } : {}),
    source: "manual",
    ...(text(data, "external_id") ? { external_id: text(data, "external_id") } : {}),
    ...(text(data, "notes") ? { notes: text(data, "notes") } : {}),
  };
}

// Reuse the key only for an exact unchanged request after an uncertain network outcome.
export function idempotentRequest<T extends object>(payload: T, previous: { signature: string; key: string } | null, createKey: () => string) {
  const signature = JSON.stringify(payload);
  const key = previous?.signature === signature ? previous.key : createKey();
  return { body: { ...payload, idempotency_key: key }, request: { signature, key } };
}
