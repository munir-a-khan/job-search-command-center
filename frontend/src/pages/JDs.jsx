import { useEffect, useState } from "react";
import { api } from "../api/client.js";

export default function JDs() {
  const [list, setList] = useState([]);
  const [raw, setRaw] = useState("");
  const [postingUrl, setPostingUrl] = useState("");
  const [source, setSource] = useState("private");
  const [busy, setBusy] = useState(false);
  const [active, setActive] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => { refresh(); }, []);
  async function refresh() { setList(await api.listJDs()); }

  async function parse() {
    setErr("");
    setBusy(true);
    try {
      const obj = await api.createJD({ raw_text: raw, posting_url: postingUrl, source });
      setActive(obj);
      setRaw("");
      setPostingUrl("");
      await refresh();
    } catch (e) { setErr(e.message); }
    setBusy(false);
  }

  async function remove(id) {
    if (!confirm("Delete this JD?")) return;
    await api.deleteJD(id);
    if (active?.id === id) setActive(null);
    await refresh();
  }

  return (
    <>
      <h2>Job Descriptions</h2>
      {err && <div className="banner">{err}</div>}
      <div className="card">
        <h3 style={{ marginTop: 0 }}>Paste a job description</h3>
        <div className="grid cols-2">
          <div><label>Posting URL (optional)</label><input value={postingUrl} onChange={(e) => setPostingUrl(e.target.value)} /></div>
          <div>
            <label>Channel</label>
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="private">Private / Company</option>
              <option value="federal">Federal (USAJOBS)</option>
              <option value="state">State (CalCareers / CalJOBS)</option>
            </select>
          </div>
        </div>
        <label>Raw JD text</label>
        <textarea style={{ minHeight: 240 }} value={raw} onChange={(e) => setRaw(e.target.value)} placeholder="Paste the full posting here…" />
        <div className="row" style={{ justifyContent: "flex-end", marginTop: 8 }}>
          <button disabled={!raw.trim() || busy} onClick={parse}>{busy ? "Parsing with Claude…" : "Parse with Claude"}</button>
        </div>
      </div>

      {active && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Parsed: {active.company} — {active.role}</h3>
          <div className="row"><span className="tag">{active.location}</span><span className="tag">{active.source}</span></div>
          <p style={{ color: "var(--muted)" }}>{active.parsed.summary}</p>
          <h3>Keywords</h3>
          <div className="row">{(active.parsed.keywords || []).map(k => <span className="tag" key={k}>{k}</span>)}</div>
          <h3>Must-have</h3>
          <ul>{(active.parsed.must_have_skills || []).map(s => <li key={s}>{s}</li>)}</ul>
          <h3>Responsibilities</h3>
          <ul>{(active.parsed.responsibilities || []).map(r => <li key={r}>{r}</li>)}</ul>
        </div>
      )}

      <h3>Saved job descriptions</h3>
      <div className="card">
        {list.length === 0 && <div className="empty">None yet.</div>}
        {list.length > 0 && (
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Source</th><th>Created</th><th></th></tr></thead>
            <tbody>
              {list.map(j => (
                <tr key={j.id}>
                  <td>{j.company || "—"}</td>
                  <td>{j.role || "—"}</td>
                  <td><span className="tag">{j.source}</span></td>
                  <td>{j.created_at?.slice(0, 10)}</td>
                  <td className="row">
                    <button className="secondary" onClick={() => setActive(j)}>View</button>
                    <button className="danger" onClick={() => remove(j.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
