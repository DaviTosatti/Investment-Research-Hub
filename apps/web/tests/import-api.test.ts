import assert from "node:assert/strict";
import test from "node:test";
import { api } from "../src/lib/api";

test("import uploads preserve binary content-type and bytes while enforcing session and CSRF headers", async t => {
  const binary = new Uint8Array([0x50, 0x4b, 0x00, 0xff]);
  t.mock.method(globalThis, "fetch", async (path: string, options: RequestInit) => {
    assert.equal(path, "/api/v1/imports?filename=original.xlsx");
    assert.equal(new Headers(options.headers).get("Content-Type"), "application/octet-stream");
    assert.equal(new Headers(options.headers).get("X-Hub-Request"), "1");
    assert.equal(options.credentials, "same-origin");
    assert.equal(options.cache, "no-store");
    assert.equal(options.body, binary);
    return Response.json({ id: "import-1" });
  });
  assert.deepEqual(await api("/imports?filename=original.xlsx", { method: "POST", headers: { "content-type": "application/octet-stream", "X-Hub-Request": "0" }, credentials: "omit", body: binary }), { id: "import-1" });
});

test("preview and confirm retain default JSON; 409 is surfaced without an automatic retry", async t => {
  let requests = 0;
  t.mock.method(globalThis, "fetch", async (_path: string, options: RequestInit) => {
    requests++;
    assert.equal(new Headers(options.headers).get("Content-Type"), "application/json");
    assert.equal(new Headers(options.headers).get("X-Hub-Request"), "1");
    assert.deepEqual(JSON.parse(String(options.body)), { preview_id: "reviewed-preview" });
    return Response.json({ error: { code: "STALE_PREVIEW", message: "Gere uma nova prévia." } }, { status: 409 });
  });
  await assert.rejects(api("/imports/import-1/confirm", { method: "POST", body: JSON.stringify({ preview_id: "reviewed-preview" }) }), { status: 409, code: "STALE_PREVIEW" });
  assert.equal(requests, 1);
});
