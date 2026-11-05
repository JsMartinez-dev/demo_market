import { useMemo, useState } from "react";
import { createApi } from "./api";
import ProductTable from "./components/ProductTable";
import RequestLog from "./components/RequestLog";
import "./index.css";

export default function App() {
  const [logs, setLogs] = useState([]);

  const api = useMemo(
    () => createApi((entry) => setLogs((prev) => [entry, ...prev].slice(0, 50))),
    []
  );

  const hits = logs.filter((l) => l.cache === "HIT").length;
  const misses = logs.filter((l) => l.cache === "MISS").length;
  const times = logs.map((l) => parseFloat(l.serverMs)).filter(Number.isFinite);
  const avg = times.length
    ? (times.reduce((a, b) => a + b, 0) / times.length).toFixed(1)
    : "—";

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">MercaDemo</div>
      </header>

      <section className="hero">
        <h1>Catálogo de productos</h1>
   
    
      </section>

      <main className="wrap">
        <div className="stats">
          <div className="stat"><b>{logs.length}</b><span>Peticiones</span></div>
          <div className="stat"><b>{hits}</b><span>Cache HIT</span></div>
          <div className="stat"><b>{misses}</b><span>Cache MISS</span></div>
          <div className="stat"><b>{avg}</b><span>ms promedio (servidor)</span></div>
        </div>

        <div className="layout">
          <section className="panel">
            <ProductTable api={api} />
          </section>
          <aside className="panel">
            <RequestLog logs={logs} />
          </aside>
        </div>
      </main>
    </div>
  );
}