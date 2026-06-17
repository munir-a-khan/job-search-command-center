import { useEffect, useState } from "react";
import { api, getApiKey, setApiKey } from "../api/client.js";

export default function ApiKeyBar() {
  const [val, setVal] = useState(getApiKey());
  const [status, setStatus] = useState(null);
  const [authRequired, setAuthRequired] = useState(false);

  useEffect(() => {
    api.health()
      .then(h => { setAuthRequired(!!h.auth_required); setStatus("ok"); })
      .catch(e => setStatus(String(e).includes("401") ? "needs-key" : "down"));
  }, [val]);

  function save() {
    setApiKey(val);
    setStatus(null);
    api.health()
      .then(h => { setAuthRequired(!!h.auth_required); setStatus("ok"); })
      .catch(e => setStatus(String(e).includes("401") ? "needs-key" : "down"));
  }

  const dot = {
    ok: { color: "var(--accent-2)", label: "connected" },
    "needs-key": { color: "var(--warn)", label: "needs key" },
    down: { color: "var(--danger)", label: "backend down" },
    null: { color: "var(--muted)", label: "checking…" },
  }[status ?? "null"];

  return (
    <div className="row" style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)", background: "var(--panel)" }}>
      <span style={{ width: 8, height: 8, borderRadius: 999, background: dot.color, display: "inline-block" }} />
      <span style={{ color: "var(--muted)", fontSize: 12 }}>{dot.label}{authRequired ? " · auth on" : " · auth off"}</span>
      <div className="row" style={{ marginLeft: "auto" }}>
        <input
          type="password"
          placeholder="X-API-Key (matches API_KEY in backend .env)"
          value={val}
          onChange={(e) => setVal(e.target.value)}
          style={{ width: 320 }}
        />
        <button className="secondary" onClick={save}>Save</button>
      </div>
    </div>
  );
}
