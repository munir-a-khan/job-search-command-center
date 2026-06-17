import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function ApplicationDetail() {
  const { id } = useParams();
  const [app, setApp] = useState(null);
  const [profile, setProfile] = useState(null);
  const [jd, setJd] = useState(null);
  const [template, setTemplate] = useState("private");
  const [extra, setExtra] = useState("");
  const [resume, setResume] = useState(null);
  const [cover, setCover] = useState(null);
  const [busy, setBusy] = useState("");
  const [err, setErr] = useState("");

  useEffect(() => { load(); }, [id]);

  async function load() {
    const a = await api.getApp(id);
    setApp(a);
    setTemplate(a.template_type || "private");
    const [p, j] = await Promise.all([api.getProfile(a.profile_id), api.getJD(a.jd_id)]);
    setProfile(p); setJd(j);
  }

  async function gen(kind) {
    setErr("");
    setBusy(kind);
    try {
      if (kind === "resume") {
        const r = await api.genResume({ application_id: Number(id), template_type: template, extra_instructions: extra });
        setResume(r);
        await load();
      } else {
        const c = await api.genCover({ application_id: Number(id), extra_instructions: extra });
        setCover(c);
        await load();
      }
    } catch (e) { setErr(e.message); }
    setBusy("");
  }

  async function patch(p) { await api.updateApp(id, p); await load(); }

  if (!app) return <div className="empty">Loading…</div>;
  return (
    <>
      <div className="row between">
        <h2>{jd?.company} — {jd?.role}</h2>
        <Link to="/applications">← back</Link>
      </div>
      {err && <div className="banner">{err}</div>}
      <div className="card">
        <div className="grid cols-3">
          <div>
            <label>Status</label>
            <select value={app.status} onChange={(e) => patch({ status: e.target.value })}>
              {["saved","applied","interview","offer","rejected","withdrawn"].map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label>Applied date</label>
            <input type="date" value={app.applied_date?.slice(0,10) || ""} onChange={(e) => patch({ applied_date: e.target.value ? new Date(e.target.value).toISOString() : null })} />
          </div>
          <div>
            <label>Follow-up date</label>
            <input type="date" value={app.follow_up_date?.slice(0,10) || ""} onChange={(e) => patch({ follow_up_date: e.target.value ? new Date(e.target.value).toISOString() : null })} />
          </div>
        </div>
        <div><label>Notes</label><textarea value={app.notes} onChange={(e) => setApp({ ...app, notes: e.target.value })} onBlur={() => patch({ notes: app.notes })} /></div>
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Generate</h3>
        <div className="row">
          <div>
            <label>Resume template</label>
            <select value={template} onChange={(e) => setTemplate(e.target.value)}>
              <option value="private">Private (1 page)</option>
              <option value="federal">Federal (USAJOBS)</option>
              <option value="state">State (CalCareers)</option>
            </select>
          </div>
        </div>
        <div><label>Extra instructions to Claude (optional)</label><input value={extra} onChange={(e) => setExtra(e.target.value)} placeholder="e.g. emphasize Linux + security clearance" /></div>
        <div className="row" style={{ marginTop: 8 }}>
          <button disabled={busy === "resume"} onClick={() => gen("resume")}>{busy === "resume" ? "Tailoring + compiling…" : "Generate resume"}</button>
          <button className="secondary" disabled={busy === "cover"} onClick={() => gen("cover")}>{busy === "cover" ? "Writing…" : "Generate cover letter"}</button>
        </div>
      </div>

      {resume && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Resume result</h3>
          <div className="row">
            <span className={"tag " + (resume.pages === 1 || template === "federal" ? "ok" : "warn")}>pages: {resume.pages}</span>
            {resume.missing_keywords?.length > 0 && <span className="tag warn">missing in PDF: {resume.missing_keywords.join(", ")}</span>}
          </div>
          {resume.warnings?.length > 0 && <div className="banner">Warnings: {resume.warnings.join(" • ")}</div>}
          <div className="row" style={{ marginTop: 8 }}>
            <a href={api.fileUrl(resume.pdf_path)} target="_blank" rel="noreferrer"><button className="secondary">Download PDF</button></a>
            <a href={api.fileUrl(resume.tex_path)} target="_blank" rel="noreferrer"><button className="secondary">Download .tex</button></a>
          </div>
          <h3>Tailored summary</h3>
          <p>{resume.summary}</p>
          <h3>Tailored bullets</h3>
          {Object.entries(resume.tailored_bullets || {}).map(([k, v]) => (
            <div key={k}>
              <h4 style={{ margin: "8px 0" }}>{k}</h4>
              <ul>{v.map((b, i) => <li key={i}>{b}</li>)}</ul>
            </div>
          ))}
        </div>
      )}

      {cover && (
        <div className="card">
          <h3 style={{ marginTop: 0 }}>Cover letter</h3>
          <pre className="preview">{cover.body}</pre>
          <a href={api.fileUrl(cover.path)} target="_blank" rel="noreferrer"><button className="secondary">Download .txt</button></a>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Job posting</h3>
        <p style={{ color: "var(--muted)" }}>{jd?.parsed?.summary}</p>
        <details><summary>Raw text</summary><pre className="preview">{jd?.raw_text}</pre></details>
      </div>
    </>
  );
}
