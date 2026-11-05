import { useState } from "react";
import ProductForm from "./ProductForm";

const money = new Intl.NumberFormat("es-CO");

const TABS = [
  { id: "consultar",label: "Consultar", hint: "Buscar por código" },
  { id: "crear", label: "Nuevo producto", hint: "Dar de alta" },
];

export default function ProductTable({ api }) {
  const [tab, setTab] = useState("consultar");
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState({ type: "", text: "" });

  const [searchId, setSearchId] = useState("");
  const [product, setProduct] = useState(null);

  const [editId, setEditId] = useState("");
  const [editing, setEditing] = useState(null);

  function changeTab(id) {
    setTab(id);
    setNotice({ type: "", text: "" });
  }

  function fail(err) {
    setNotice({ type: "error", text: err.message });
  }

  async function lookup(id, onFound) {
    const clean = id.trim();
    if (!clean) return;
    setBusy(true);
    setNotice({ type: "", text: "" });
    try {
      onFound(await api.get(clean));
    } catch (err) {
      onFound(null);
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  async function save(form) {
    const isUpdate = tab === "editar";
    setBusy(true);
    setNotice({ type: "", text: "" });
    try {
      if (isUpdate) {
        const saved = await api.update(editing.product_id, form);
        setEditing(saved);
        setNotice({ type: "success", text: `Producto ${saved.product_id} actualizado` });
      } else {
        const saved = await api.create(form);
        setProduct(saved);
        setSearchId(saved.product_id);
        setTab("consultar");
        setNotice({ type: "success", text: `Producto ${saved.product_id} creado` });
      }
    } catch (err) {
      fail(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={`tab ${tab === t.id ? "active" : ""}`}
            onClick={() => changeTab(t.id)}
          >
            <span className="icon">{t.icon}</span>
            <strong>{t.label}</strong>
            <small>{t.hint}</small>
          </button>
        ))}
      </nav>

      {notice.text && <p className={`alert ${notice.type}`}>{notice.text}</p>}

      {tab === "consultar" && (
        <>
          <SearchBar
            value={searchId}
            onChange={setSearchId}
            onSubmit={() => lookup(searchId, setProduct)}
            busy={busy}
            buttonText="Buscar"
          />
          {product ? (
            <Ficha
              product={product}
              onEdit={() => {
                setEditId(product.product_id);
                setEditing(product);
                changeTab("editar");
              }}
            />
          ) : (
            <Empty text="Escribe el código de un producto para ver su ficha." />
          )}
        </>
      )}

      {tab === "crear" && (
        <>
          <h2 className="section-title">Alta de producto</h2>
          <ProductForm busy={busy} submitLabel="Crear producto" onSubmit={save} />
        </>
      )}

      {tab === "editar" && (
        <>
          <SearchBar
            value={editId}
            onChange={setEditId}
            onSubmit={() => lookup(editId, setEditing)}
            busy={busy}
            buttonText="Cargar"
            placeholder="Código del producto a actualizar..."
          />
          {editing ? (
            <ProductForm
              key={editing.product_id}
              initial={editing}
              isEdit
              busy={busy}
              submitLabel="Guardar cambios"
              onSubmit={save}
            />
          ) : (
            <Empty text="Carga un producto por su código para editarlo." />
          )}
        </>
      )}
    </>
  );
}

function SearchBar({ value, onChange, onSubmit, busy, buttonText, placeholder }) {
  function handle(e) {
    e.preventDefault();
    onSubmit();
  }
  return (
    <form className="search-row" onSubmit={handle}>
      <input
        className="input"
        placeholder={placeholder ?? "Código del producto, ej. LEC-001..."}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      <button type="submit" className="btn primary" disabled={busy}>
        {buttonText}
      </button>
    </form>
  );
}

function Ficha({ product, onEdit }) {
  const lowStock = product.stock < 10;
  return (
    <div className="ficha">
      <div className="ficha-head">
        <div>
          <span className="code">{product.product_id}</span>
          <h2>{product.name}</h2>
          <p className="muted">{product.category}</p>
        </div>
        <button className="btn accent" onClick={onEdit}>Editar</button>
      </div>

      <div className="tiles">
        <div className="tile">
          <span>Precio</span>
          <b>$ {money.format(product.price)}</b>
        </div>
        <div className={`tile ${lowStock ? "warn" : ""}`}>
          <span>Stock</span>
          <b>{product.stock} uds</b>
        </div>
        <div className={`tile ${lowStock ? "warn" : "ok"}`}>
          <span>Estado</span>
          <b>{lowStock ? "Stock bajo" : "Disponible"}</b>
        </div>
      </div>
    </div>
  );
}

function Empty({ text }) {
  return <div className="empty">{text}</div>;
}