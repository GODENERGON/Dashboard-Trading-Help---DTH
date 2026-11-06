// Client of the local Dabitur engine (Python sidecar, ADR 0003).
// Inside the desktop app the shell tells us the port and the token; in a browser
// (npm run dev) we talk to `make api` on 127.0.0.1:8765 without a token.
import { invoke, isTauri } from "@tauri-apps/api/core";

type Conn = { base: string; token: string | null };
let conn: Promise<Conn> | null = null;

export const inDesktop = isTauri();

function connection(): Promise<Conn> {
  conn ??= (async () => {
    if (inDesktop) {
      const c = await invoke<{ port: number; token: string }>("backend_config");
      return { base: `http://127.0.0.1:${c.port}`, token: c.token };
    }
    return { base: import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8765", token: null };
  })();
  return conn;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { base, token } = await connection();
  const headers = new Headers(init.headers);
  if (token) headers.set("X-Dabitur-Token", token);
  if (init.body) headers.set("Content-Type", "application/json");
  const res = await fetch(base + path, { ...init, headers });
  if (!res.ok) throw new Error(`${res.status} ${path}`);
  return (await res.json()) as T;
}

/** Wait for the engine to answer /health (the packaged sidecar needs a few seconds). */
export async function waitForEngine(timeoutMs: number): Promise<boolean> {
  const end = Date.now() + timeoutMs;
  while (Date.now() < end) {
    try {
      await api("/health");
      return true;
    } catch {
      await new Promise((r) => setTimeout(r, 500));
    }
  }
  return false;
}

export async function openExternal(url: string): Promise<void> {
  if (inDesktop) {
    const { openUrl } = await import("@tauri-apps/plugin-opener");
    await openUrl(url);
  } else {
    window.open(url, "_blank", "noopener");
  }
}

export type DataStatus = {
  as_of: string; source: string; fetched_at: string | null; refreshing: boolean;
  failures: number; last_error: string | null;
};

// Small, failure-tolerant wrapper around localStorage (it can be unavailable).
export const prefs = {
  get(key: string): string | null {
    try { return localStorage.getItem(`dabitur.${key}`); } catch { return null; }
  },
  set(key: string, value: string): void {
    try { localStorage.setItem(`dabitur.${key}`, value); } catch { /* ignore */ }
  },
};
