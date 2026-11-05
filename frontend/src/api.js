const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8090/api";

export function createApi(onLog) {
  async function request(method, path, body) {
    const start = performance.now();
    const res = await fetch(`${BASE}${path}`, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
    const clientMs = performance.now() - start;

    onLog?.({
      id: crypto.randomUUID(),
      time: new Date().toLocaleTimeString(),
      method,
      path,
      status: res.status,
      cache: res.headers.get("X-Cache") ?? "-",
      serverMs: res.headers.get("X-Process-Time-Ms") ?? "-",
      clientMs: clientMs.toFixed(1),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      // FastAPI devuelve detail como texto (errores de negocio) o como lista (errores de validación)
      const msg = Array.isArray(err.detail)
        ? err.detail.map((d) => `${d.loc.at(-1)}: ${d.msg}`).join(" · ")
        : err.detail ?? `Error ${res.status}`;
      throw new Error(msg);
    }
    return res.json();
  }

  return {
    get: (productId) =>
      request("GET", `/products/${encodeURIComponent(productId)}`),
    create: (data) => request("POST", "/products", data),
    update: (productId, data) =>
      request("PUT", `/products/${encodeURIComponent(productId)}`, data),
  };
}