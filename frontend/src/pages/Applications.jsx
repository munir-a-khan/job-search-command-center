import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function Applications() {
  const [apps, setApps] = useState([]);
  const [profiles, setProfiles] = useState([]);
  const [jds, setJds] = useState([]);
  const [profileId, setProfileId] = useState("");
  const [jdId, setJdId] = useState("");
  const [template, setTemplate] = useState("private");
  const [err, setErr] = useState("");

  useEffect(() => { refresh(); }, []);

  async function refresh() {
    const [a, p, j] = await Promise.all([api.listApps(), api.listProfiles(), api.listJDs()]);
    setApps(a); setProfiles(p); setJds(j);
    if (!profileId && p.length) setProfileId(String(p[0].id));
    if (!jdId && j.length) setJdId(String(j[0].id));
  }

  async function create() {
    setErr("");
    if (!profileId || !jdId) { setErr("Pick a profile and a JD first."); return; }
    try {
      await api.createApp({
        profile_id: Number(profileId),
        jd_id: Number(jdId),
        template_type: template,
      });
      await refresh();
    } catch (e) { setErr(e.message); }
  }

  async function update(id, patch) { await api.updateApp(id, patch); await refresh(); }
  async function remove(id) {
    if (!confirm("Delete this application?")) return;
    await api.deleteApp(id); await refresh();
  }

  const jdById = Object.fromEntries(jds.map(j => [j.id, j]));
  const profileById = Object.fromEntries(profiles.map(p => [p.id, p]));

  return (
    <>
      <h2>Applications</h2>
      {err && <div className="banner">{err}</div>}
      <div className="card">
        <h3 style={{ marginTop: 0 }}>New application</h3>
        <div className="grid cols-3">
          <div>
            <label>Profile</label>
            <select value={profileId} onChange={(e) => setProfileId(e.target.value)}>
              <option value="">(pick)</option>
              {profiles.map(p => <option key={p.id} value={p.id}>{p.full_name}</option>)}
            </select>
          </div>
          <div>
            <label>Job description</label>
            <select value={jdId} onChange={(e) => setJdId(e.target.value)}>
              <option value="">(pick)</option>
              {jds.map(j => <option key={j.id} value={j.id}>{j.company} — {j.role}</option>)}
            </select>
          </div>
          <div>
            <label>Resume template</label>
            <select value={template} onChange={(e) => setTemplate(e.target.value)}>
              <option value="private">Private</option>
              <option value="federal">Federal</option>
              <option value="state">State</option>
            </select>
          </div>
        </div>
        <div className="row" style={{ justifyContent: "flex-end", marginTop: 8 }}>
          <button onClick={create} disabled={!profileId || !jdId}>Create</button>
        </div>
      </div>

      <div className="card">
        {apps.length === 0 && <div className="empty">No applications yet.</div>}
        {apps.length > 0 && (
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Applied</th><th>Follow-up</th><th>Template</th><th></th></tr></thead>
            <tbody>
              {apps.map(a => {
                const jd = jdById[a.jd_id];
                const prof = profileById[a.profile_id];
                return (
                  <tr key={a.id}>
                    <td>{jd?.company || "—"}<div style={{ color: "var(--muted)", fontSize: 11 }}>{prof?.full_name}</div></td>
                    <td>{jd?.role || "—"}</td>
                    <td>
                      <select value={a.status} onChange={(e) => update(a.id, { status: e.target.value })}>
                        {["saved","applied","interview","offer","rejected","withdrawn"].map(s => <option key={s} value={s}>{s}</option>)}
                      </select>
                    </td>
                    <td><input type="date" value={a.applied_date?.slice(0,10) || ""} onChange={(e) => update(a.id, { applied_date: e.target.value ? new Date(e.target.value).toISOString() : null })} /></td>
                    <td><input type="date" value={a.follow_up_date?.slice(0,10) || ""} onChange={(e) => update(a.id, { follow_up_date: e.target.value ? new Date(e.target.value).toISOString() : null })} /></td>
                    <td><span className="tag">{a.template_type}</span></td>
                    <td className="row">
                      <Link to={`/applications/${a.id}`}><button className="secondary">Open</button></Link>
                      <button className="danger" onClick={() => remove(a.id)}>X</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
