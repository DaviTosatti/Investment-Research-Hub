import assert from "node:assert/strict";
import test from "node:test";
import { allPages, api, ApiError, filterQuery, positionsCsv } from "../src/lib/api";

const filters = { owner_id: "owner-id", portfolio_id: "portfolio-id", as_of: "2026-11-04" };

test("every mutation uses the hub request header, same-origin cookies and exact JSON strings", async t => {
  const seen: RequestInit[] = [];
  t.mock.method(globalThis, "fetch", async (_url: unknown, options: RequestInit) => {
    seen.push(options);
    return new Response(null, { status: 204 });
  });
  for (const method of ["post", "PUT", "PATCH", "DELETE"]) {
    await api("/prices", { method, body: JSON.stringify({ price: "0.12345678" }), headers: { "X-Hub-Request": "0" }, credentials: "omit" });
  }
  for (const options of seen) {
    assert.equal(new Headers(options.headers).get("X-Hub-Request"), "1");
    assert.equal(new Headers(options.headers).get("Content-Type"), "application/json");
    assert.equal(options.credentials, "same-origin");
    assert.equal(options.cache, "no-store");
    assert.equal(JSON.parse(String(options.body)).price, "0.12345678");
  }
});

test("selectors load beyond both the default and maximum API page sizes", async t => {
  const records = Array.from({ length: 453 }, (_, id) => ({ id: String(id) }));
  const offsets: number[] = [];
  t.mock.method(globalThis, "fetch", async (input: string) => {
    const query = new URL(input, "http://localhost").searchParams;
    const offset = Number(query.get("offset"));
    offsets.push(offset);
    assert.equal(query.get("limit"), "200");
    assert.equal(query.get("owner_id"), "owner-id");
    return Response.json({ items: records.slice(offset, offset + 200), total: records.length, limit: 200, offset });
  });
  assert.deepEqual(await allPages("/portfolios?owner_id=owner-id", new AbortController().signal), records);
  assert.deepEqual(offsets, [0, 200, 400]);
});

test("an incomplete or mismatched page fails instead of presenting a truncated selector", async t => {
  t.mock.method(globalThis, "fetch", async () => Response.json({ items: [], total: 5, limit: 200, offset: 0 }));
  await assert.rejects(allPages("/owners", new AbortController().signal), { code: "incomplete_list" });
  t.mock.method(globalThis, "fetch", async () => Response.json({ items: [{ id: "1" }], total: 5, limit: 200, offset: 200 }));
  await assert.rejects(allPages("/owners", new AbortController().signal), { code: "incomplete_list" });
});

test("cancellation discards an uncancellable reference response and stops pagination", async t => {
  const controller = new AbortController();
  let calls = 0;
  let release!: (response: Response) => void;
  t.mock.method(globalThis, "fetch", () => { calls++; return new Promise<Response>(resolve => { release = resolve; }); });
  const pending = allPages("/owners", controller.signal);
  controller.abort();
  release(Response.json({ items: [{ id: "old-owner" }], total: 400, limit: 200, offset: 0 }));
  await assert.rejects(pending, { name: "AbortError" });
  assert.equal(calls, 1);
});

test("CSV uses exactly the displayed filters and engine snapshot with cookie authentication", async t => {
  t.mock.method(globalThis, "fetch", async (input: string, options: RequestInit) => {
    const url = new URL(input, "http://localhost");
    assert.equal(url.pathname, "/api/v1/reports/positions.csv");
    assert.deepEqual(Object.fromEntries(url.searchParams), { ...filters, snapshot_id: "snapshot-abc" });
    assert.equal(options.credentials, "same-origin");
    assert.equal(options.cache, "no-store");
    return new Response("ativo;custo_brl\nTEST3;0.12345678\n", { headers: { "Content-Type": "text/csv" } });
  });
  const blob = await positionsCsv(filters, "snapshot-abc", new AbortController().signal);
  assert.equal(await blob.text(), "ativo;custo_brl\nTEST3;0.12345678\n");
});

test("a changed or absent snapshot blocks export without silently retrying a different snapshot", async t => {
  let calls = 0;
  t.mock.method(globalThis, "fetch", async () => {
    calls++;
    return Response.json({ error: { code: "SNAPSHOT_CHANGED", message: "Atualize o painel." } }, { status: 409 });
  });
  await assert.rejects(positionsCsv(filters, "old-snapshot", new AbortController().signal), (error: unknown) => error instanceof ApiError && error.status === 409 && error.code === "SNAPSHOT_CHANGED");
  await assert.rejects(positionsCsv(filters, "", new AbortController().signal), { code: "SNAPSHOT_CHANGED" });
  assert.equal(calls, 1);
});

test("a late CSV response is discarded when its selection is no longer active", async t => {
  const controller = new AbortController();
  let release!: (response: Response) => void;
  t.mock.method(globalThis, "fetch", () => new Promise<Response>(resolve => { release = resolve; }));
  const pending = positionsCsv(filters, "old-snapshot", controller.signal);
  controller.abort();
  release(new Response("stale csv"));
  await assert.rejects(pending, { name: "AbortError" });
});

test("expired sessions signal a redirect while invalid login credentials keep the login form active", async t => {
  const browser = new EventTarget();
  let expired = 0;
  browser.addEventListener("hub:session-expired", () => { expired++; });
  Object.defineProperty(globalThis, "window", { configurable: true, value: browser });
  t.after(() => { Reflect.deleteProperty(globalThis, "window"); });
  t.mock.method(globalThis, "fetch", async () => Response.json({ error: { code: "UNAUTHENTICATED", message: "Entre novamente." } }, { status: 401 }));
  await assert.rejects(api("/auth/login", { method: "POST", body: "{}" }), { status: 401 });
  assert.equal(expired, 0);
  await assert.rejects(api("/auth/session"), { status: 401 });
  assert.equal(expired, 1);
});

test("non-JSON failures remain typed errors and empty filters are omitted", async t => {
  t.mock.method(globalThis, "fetch", async () => new Response("upstream unavailable", { status: 502 }));
  await assert.rejects(api("/dashboard"), { status: 502, code: "request_failed" });
  assert.equal(filterQuery({ owner_id: "", portfolio_id: "", as_of: "2026-11-04" }), "as_of=2026-11-04");
});
