export default function RequestLog({ logs }) {
  return (
    <>
      <h3>Peticiones</h3>
      <p className="hint">Tiempos de cada llamada. Revisa la terminal del backend para ver los pasos internos.</p>

      <ul className="log">
        {logs.map((l) => (
          <li key={l.id}>
            <div className="row">
              <span className={`method ${l.method.toLowerCase()}`}>{l.method}</span>
              <code>{l.path}</code>
              <span className="time">{l.time}</span>
            </div>
            <div className="row meta">
              <span className={`badge ${l.cache === "HIT" ? "hit" : l.cache === "MISS" ? "miss" : ""}`}>
                {l.cache}
              </span>
              <span>servidor: <b>{l.serverMs} ms</b></span>
              <span>cliente: <b>{l.clientMs} ms</b></span>
              <span>HTTP {l.status}</span>
            </div>
          </li>
        ))}
        {logs.length === 0 && <li className="hint">Aún no hay peticiones.</li>}
      </ul>
    </>
  );
}