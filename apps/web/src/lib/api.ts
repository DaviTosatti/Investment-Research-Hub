import type { Filters, PageResult } from "./types";

export class ApiError extends Error {
  constructor(public readonly status: number, public readonly code: string, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request(path: string, options: RequestInit = {}): Promise<Response> {
  const headers = new Headers(options.headers);
  const method = (options.method ?? "GET").toUpperCase();
  if (!["GET", "HEAD", "OPTIONS"].includes(method)) headers.set("X-Hub-Request", "1");
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const response = await fetch(`/api/v1${path}`, {
    ...options, method, headers, credentials: "same-origin", cache: "no-store",
  });
  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const detail = body && typeof body === "object" && "error" in body ? body.error : null;
    const message = detail && typeof detail === "object" && "message" in detail && typeof detail.message === "string" ? detail.message : "";
    const code = detail && typeof detail === "object" && "code" in detail && typeof detail.code === "string" ? detail.code : "request_failed";
    if (response.status === 401 && path !== "/auth/login" && typeof window !== "undefined") {
      window.dispatchEvent(new Event("hub:session-expired"));
    }
    throw new ApiError(response.status, code, message);
  }
  return response;
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await request(path, options);
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

// The export must refer to the exact engine snapshot currently displayed.
export async function positionsCsv(filters: Filters, snapshotId: string, signal: AbortSignal): Promise<Blob> {
  if (!snapshotId) throw new ApiError(409, "SNAPSHOT_CHANGED", "");
  const query = new URLSearchParams(filterQuery(filters));
  query.set("snapshot_id", snapshotId);
  const response = await request(`/reports/positions.csv?${query}`, { signal });
  const blob = await response.blob();
  signal.throwIfAborted();
  return blob;
}

export function filterQuery(filters: Filters): string {
  const query = new URLSearchParams();
  if (filters.owner_id) query.set("owner_id", filters.owner_id);
  if (filters.portfolio_id) query.set("portfolio_id", filters.portfolio_id);
  if (filters.as_of) query.set("as_of", filters.as_of);
  return query.toString();
}

// Reference selectors must include every page, rather than silently truncate at 100 rows.
export async function allPages<T>(path: string, signal: AbortSignal): Promise<T[]> {
  const items: T[] = [];
  let offset = 0;
  for (;;) {
    signal.throwIfAborted();
    const query = new URLSearchParams(path.split("?")[1]);
    query.set("limit", "200");
    query.set("offset", String(offset));
    const page = await api<PageResult<T>>(`${path.split("?")[0]}?${query}`, { signal });
    signal.throwIfAborted();
    if (page.offset !== offset) throw new ApiError(502, "incomplete_list", "");
    items.push(...page.items);
    offset += page.items.length;
    if (offset >= page.total) return items;
    if (page.items.length === 0) throw new ApiError(502, "incomplete_list", "");
  }
}
