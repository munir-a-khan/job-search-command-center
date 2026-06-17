import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client.js";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [health, setHealth] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.health().then(setHealth).catch(e => setErr(e.message));
    api.dashboard().then(setData).catch(e => setErr(e.message));
  }, []);

  if (err) return <div className="banner">Could not load: {err}</div>;
  if (!data) return <div className="empty">Loading…</div>;

  const statuses = ["saved", "applied", "interview", "offer", "rejected", "withdrawn"];
  return (
    <>
      <h2>Pipeline Dashboard</h2>
      {health && !health.claude_configured && (
        <div className="banner">
          ANTHROPIC_API_KEY is not configured. Add it to backend/.env to enable AI features.
        </div>
      )}
      <div className="grid cols-3">
        <div className="kpi"><div className="l">Total applications</div><div className="n">{data.total}</div></div>
        <div className="kpi"><div className="l">Follow-ups due (3 days)</div><div className="n">{data.follow_ups_due}</div></div>
        <div className="kpi"><div className="l">Active (applied + interview)</div><div className="n">{(data.by_status.applied || 0) + (data.by_status.interview || 0)}</div></div>
      </div>

      <h3>Status breakdown</h3>
      <div className="card row">
        {statuses.map(s => (
          <span key={s} className={"tag " + (s === "offer" ? "ok" : s === "rejected" ? "danger" : "")}>
            {s}: {data.by_status[s] || 0}
          </span>
        ))}
      </div>

      <h3>Recent activity</h3>
      <div className="card">
        {data.recent.length === 0 && <div className="empty">No applications yet. Create one from the Applications page.</div>}
        {data.recent.length > 0 && (
          <table>
            <thead><tr><th>Company</th><th>Role</th><th>Status</th><th>Applied</th><th>Follow-up</th><th>Updated</th><th></th></tr></thead>
            <tbody>
              {data.recent.map(r => (
                <tr key={r.id}>
                  <td>{r.company || "—"}</td>
                  <td>{r.role || "—"}</td>
                  <td><span className="tag">{r.status}</span></td>
                  <td>{r.applied_date?.slice(0, 10) || "—"}</td>
                  <td>{r.follow_up_date?.slice(0, 10) || "—"}</td>
                  <td>{r.updated_at?.slice(0, 10)}</td>
                  <td><Link to={`/applications/${r.id}`}>Open</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
