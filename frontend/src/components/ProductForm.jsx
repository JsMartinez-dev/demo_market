import { useState } from "react";

const EMPTY = { product_id: "", name: "", category: "", price: "", stock: "" };

export default function ProductForm({ initial = {}, isEdit = false, busy, submitLabel, onSubmit }) {
  const [form, setForm] = useState({ ...EMPTY, ...initial });

  const set = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit({
      product_id: form.product_id.trim(),
      name: form.name.trim(),
      category: form.category.trim(),
      price: parseInt(form.price, 10),
      stock: parseInt(form.stock, 10),
    });
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="grid-2">
        <Field label="Código" full>
          <input
            name="product_id"
            value={form.product_id}
            onChange={set}
            disabled={isEdit}
            required
            minLength={3}
            maxLength={64}
            pattern="[A-Za-z0-9_\-]+"
            title="Solo letras, números, guion y guion bajo"
          />
        </Field>

        <Field label="Nombre" full>
          <input name="name" value={form.name} onChange={set} required minLength={2} maxLength={120} />
        </Field>

        <Field label="Categoría" full>
          <input name="category" value={form.category} onChange={set} required minLength={5} maxLength={120} />
        </Field>

        <Field label="Precio (entero)">
          <input name="price" type="number" step="1" min="0" value={form.price} onChange={set} required />
        </Field>

        <Field label="Stock">
          <input name="stock" type="number" step="1" min="0" value={form.stock} onChange={set} required />
        </Field>
      </div>

      <div className="actions">
        <button type="submit" className="btn primary" disabled={busy}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
}

function Field({ label, full, children }) {
  return (
    <label className={`field ${full ? "full" : ""}`}>
      <span>{label}</span>
      {children}
    </label>
  );
}