import assert from "node:assert/strict";
import test from "node:test";
import { date, money, number, percent, serverMessage, today, unitPrice } from "../src/lib/format";

test("financial formatting preserves decimal strings beyond floating-point precision", () => {
  assert.equal(money("9007199254740993.12", "pt").replaceAll("\u00a0", " "), "R$ 9.007.199.254.740.993,12");
  assert.equal(number("9999999999.12345678", "pt"), "9.999.999.999,12345678");
  assert.equal(number("9999999999.12345678", "en"), "9,999,999,999.12345678");
  assert.equal(percent("12.34", "pt"), "12,34%");
});

test("missing market values stay unavailable rather than appearing as zero", () => {
  for (const value of [null, undefined, "", "NaN", "Infinity"]) {
    assert.equal(money(value, "pt"), "Indisponível");
    assert.equal(unitPrice(value, "pt"), "Indisponível");
    assert.equal(number(value, "en"), "Unavailable");
  }
  assert.notEqual(money("0", "pt"), "Indisponível");
  assert.equal(date(null, "en"), "Unavailable");
});

test("date-only references do not shift and the business day matches the API timezone", () => {
  assert.equal(date("2026-11-04", "pt"), "04/11/2026");
  assert.equal(date("2026-11-04", "en"), "04/11/2026");
  assert.equal(today(new Date("2026-11-05T02:59:59Z")), "2026-11-04");
  assert.equal(today(new Date("2026-11-05T03:00:00Z")), "2026-11-05");
});

test("timestamps use São Paulo time, including the previous calendar day around UTC midnight", () => {
  assert.equal(date("2026-11-05T02:30:00Z", "pt", true), "04/11/2026, 23:30");
  assert.equal(date("2026-11-05T02:30:00Z", "en", true), "04/11/2026, 23:30");
  assert.equal(date("2026-11-05T03:30:00Z", "pt", true), "05/11/2026, 00:30");
  assert.equal(date("2026-11-05T02:30:00Z", "pt"), "04/11/2026");
  assert.equal(date("2026-11-04T23:30:00-03:00", "pt", true), "04/11/2026, 23:30");
});

test("unit prices preserve tiny quotes and eight decimal places while cash stays in cents", () => {
  const spaces = (value: string) => value.replaceAll("\u00a0", " ");
  assert.equal(spaces(unitPrice("0.00000001", "pt")), "R$ 0,00000001");
  assert.equal(spaces(unitPrice("0.00000001", "en")), "R$0.00000001");
  assert.equal(spaces(unitPrice("9999999999.12345678", "pt")), "R$ 9.999.999.999,12345678");
  assert.equal(spaces(unitPrice("12.34000000", "pt")), "R$ 12,34");
  assert.equal(spaces(unitPrice("0", "pt")), "R$ 0,00");
  assert.equal(spaces(money("0.00000001", "pt")), "R$ 0,00");
  assert.equal(spaces(money("12.34567890", "pt")), "R$ 12,35");
});

test("English retains split-invalidated and stale quote evidence and trade-date cash semantics", () => {
  assert.equal(serverMessage("TEST3: registre uma avaliação após o desdobramento.", "en"), "TEST3: record a valuation after the split.");
  assert.equal(serverMessage("TEST3: avaliação desatualizada.", "en"), "TEST3: stale valuation.");
  assert.equal(serverMessage("Caixa reconhecido por data de negociação; não representa saldo liquidado para saque.", "en"), "Trade-date cash; this does not represent a settled balance available for withdrawal.");
  assert.equal(serverMessage("Nova evidência do servidor.", "en"), "Nova evidência do servidor.");
});
