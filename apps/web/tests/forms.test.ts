import assert from "node:assert/strict";
import test from "node:test";
import { api } from "../src/lib/api";
import { decimal, DecimalInputError, idempotentRequest, transactionPayload } from "../src/lib/forms";

function form(values: Record<string, string>) {
  const result = new FormData();
  for (const [key, value] of Object.entries(values)) result.set(key, value);
  return result;
}

test("decimal input preserves eight places and accepts a pt-BR comma or decimal point", () => {
  assert.equal(decimal(form({ amount: " 9999999999,12345678 " }), "amount"), "9999999999.12345678");
  assert.equal(decimal(form({ amount: "0,00000001" }), "amount"), "0.00000001");
  assert.equal(decimal(form({ amount: "12.3400" }), "amount"), "12.3400");
  assert.equal(decimal(form({}), "amount"), "");
});

test("ambiguous grouping, signed values, exponent notation and excess precision are rejected", () => {
  for (const value of ["1.234,56", "1,234.56", "1 000", "-1", "+1", "1e3", "NaN", "Infinity", ".5", "1,", "1,123456789", "1\n2"]) {
    assert.throws(() => decimal(form({ amount: value }), "amount"), DecimalInputError, value);
  }
});

test("a buy sends exact strings without deriving its gross amount in the frontend", () => {
  const payload = transactionPayload(form({
    portfolio_id: "portfolio-id", instrument_id: "instrument-id", event_type: "buy",
    quantity: "1234567890,12345678", unit_price: "0,00000001", fees: "0,20", taxes: "0",
    gross_amount: "999", trade_date: "2026-11-04", notes: "  Registro conferido  ",
  }));
  assert.deepEqual(payload, {
    portfolio_id: "portfolio-id", event_type: "buy", instrument_id: "instrument-id",
    quantity: "1234567890.12345678", unit_price: "0.00000001", fees: "0.20", taxes: "0",
    trade_date: "2026-11-04", source: "manual", notes: "Registro conferido",
  });
});

test("cash events and splits omit irrelevant amounts and preserve optional references", () => {
  const deposit = transactionPayload(form({
    portfolio_id: "portfolio-id", event_type: "deposit", gross_amount: "1000,50",
    trade_date: "2026-11-04", settlement_date: "2026-11-05", external_id: "REF-1",
  }));
  assert.deepEqual(deposit, {
    portfolio_id: "portfolio-id", event_type: "deposit", gross_amount: "1000.50",
    fees: "0", taxes: "0", trade_date: "2026-11-04", settlement_date: "2026-11-05",
    source: "manual", external_id: "REF-1",
  });
  const split = transactionPayload(form({ event_type: "split", quantity: "2,5", gross_amount: "999", unit_price: "999" }));
  assert.equal(split.quantity, "2.5");
  assert.equal("unit_price" in split, false);
  assert.equal("gross_amount" in split, false);
});

test("a network retry submits the same idempotency key; an edited or completed event gets a new key", async t => {
  const bodies: string[] = [];
  t.mock.method(globalThis, "fetch", async (_url: unknown, options: RequestInit) => {
    bodies.push(String(options.body));
    if (bodies.length === 1) throw new TypeError("Connection lost after sending the request");
    return Response.json({ id: "persisted-event" });
  });
  const payload = transactionPayload(form({ event_type: "deposit", gross_amount: "12,50", trade_date: "2026-11-04" }));
  let sequence = 0;
  const createKey = () => `request-key-${++sequence}`;
  const first = idempotentRequest(payload, null, createKey);
  await assert.rejects(api("/transactions", { method: "POST", body: JSON.stringify(first.body) }), TypeError);
  const retry = idempotentRequest(transactionPayload(form({ event_type: "deposit", gross_amount: "12.50", trade_date: "2026-11-04" })), first.request, createKey);
  assert.deepEqual(await api("/transactions", { method: "POST", body: JSON.stringify(retry.body) }), { id: "persisted-event" });
  assert.equal(bodies[0], bodies[1]);
  assert.equal(sequence, 1);
  const edited = idempotentRequest({ ...payload, gross_amount: "12.51" }, retry.request, createKey);
  assert.notEqual(edited.request.key, retry.request.key);
  const nextEvent = idempotentRequest(payload, null, createKey);
  assert.notEqual(nextEvent.request.key, first.request.key);
});
