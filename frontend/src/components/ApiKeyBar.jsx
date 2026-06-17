import { useEffect, useState } from "react";
import { api, getApiKey, setApiKey, clearStoredKey } from "../api/client.js";

export default function ApiKeyBar() {
  const [val, setVal] = useState(getApiKey());
  const [status, setStatus] = useState(null);
  const [authRequired, setAuthRequired] = useState(false);

  function check() {
    setStatus(null);
    api.health()
      .then(h => { setAuthRequired(!!h.auth_required); setStatus("ok"); })
      .catch(e => setStatus(String(e).includes("401") ? "needs-key" : "down"));
  }

  useEffect(() => { check(); }, []);

  function save() {
    setApiKey(val);
    check();
  }

  function reset() {
    clearStoredKey();
    const envKey = getApiKey(); // falls back to VITE_API_KEY
    setVal(envKey);
    check();
  }

  const dot = {
    ok:          { color: "var(--accent-2)", label: "connected" },
    "needs-key": { color: "var(--warn)",    label: "wrong key" },
    down:        { color: "var(--danger)",  label: "backend down" },
    null:        { color: "var(--muted)",   label: "checking…" },
  }[status ?? "null"];

  return (
    <div className="row" style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)", background: "var(--panel)" }}>
      <span style={{ width: 8, height: 8, borderRadius: 999, background: dot.color, display: "inline-block" }} />
      <span style={{ color: "var(--muted)", fontSize: 12 }}>
        {dot.label}{authRequired ? " · auth on" : " · auth off"}
      </span>
      <div className="row" style={{ marginLeft: "auto", gap: 6 }}>
        <input
          type="password"
          placeholder="App password (API_KEY in .env — auto-loaded if VITE_API_KEY set)"
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && save()}
          style={{ width: 300 }}
        />
        <button className="secondary" onClick={save}>Save</button>
        <button className="secondary" onClick={reset} title="Reset to .env default">↺</button>
      </div>
    </div>
  );
}
