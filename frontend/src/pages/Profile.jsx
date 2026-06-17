import { useEffect, useState } from "react";
import { api } from "../api/client.js";

const emptyProfile = {
  full_name: "",
  email: "",
  phone: "",
  location: "",
  linkedin: "",
  github: "",
  website: "",
  summary: "",
  education: [],
  work_history: [],
  projects: [],
  skills: {},
  certifications: [],
};

const emptyEdu = { school: "", degree: "", location: "", start: "", end: "", gpa: "", coursework: "", honors: "" };
const emptyWork = { title: "", company: "", location: "", start: "", end: "", hours_per_week: "", salary: "", supervisor: "", may_contact: "Yes", bullets: [] };
const emptyProject = { name: "", focus: "", date: "", bullets: [] };

export default function Profile() {
  const [profiles, setProfiles] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  const [p, setP] = useState(emptyProfile);
  const [status, setStatus] = useState("");
  const [skillsRows, setSkillsRows] = useState([{ k: "", v: "" }]);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [uploadErr, setUploadErr] = useState("");

  useEffect(() => { refresh(); }, []);

  async function refresh() {
    const list = await api.listProfiles();
    setProfiles(list);
    if (list.length && !currentId) load(list[0].id);
  }

  async function load(id) {
    const data = await api.getProfile(id);
    setCurrentId(id);
    setP(data);
    const sk = Object.entries(data.skills || {});
    setSkillsRows(sk.length ? sk.map(([k, v]) => ({ k, v })) : [{ k: "", v: "" }]);
  }

  function setField(k, v) { setP({ ...p, [k]: v }); }

  function commitSkills(rows) {
    const obj = {};
    rows.forEach(({ k, v }) => { if (k.trim()) obj[k.trim()] = v; });
    return obj;
  }

  async function save() {
    setStatus("Saving…");
    const payload = { ...p, skills: commitSkills(skillsRows) };
    try {
      if (currentId) {
        const out = await api.updateProfile(currentId, payload);
        setP(out);
        setStatus("Saved.");
      } else {
        const out = await api.createProfile(payload);
        setCurrentId(out.id);
        setP(out);
        await refresh();
        setStatus("Created.");
      }
    } catch (e) { setStatus("Error: " + e.message); }
    setTimeout(() => setStatus(""), 2500);
  }

  function newProfile() {
    setCurrentId(null);
    setP(emptyProfile);
    setSkillsRows([{ k: "", v: "" }]);
  }

  async function handleResumeUpload(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";
    setUploadErr("");
    setUploadBusy(true);
    try {
      const data = await api.profileFromResume(file);
      setP({ ...emptyProfile, ...data });
      const sk = Object.entries(data.skills || {});
      setSkillsRows(sk.length ? sk.map(([k, v]) => ({ k, v })) : [{ k: "", v: "" }]);
      setCurrentId(null);
      setStatus("Resume parsed — review the fields and click Save.");
    } catch (err) {
      setUploadErr(err.message);
    }
    setUploadBusy(false);
  }

  async function remove() {
    if (!currentId) return;
    if (!confirm("Delete this profile? Applications referencing it will be orphaned.")) return;
    await api.deleteProfile(currentId);
    setCurrentId(null);
    setP(emptyProfile);
    await refresh();
  }

  function arrField(field, idx, key, val) {
    const next = [...p[field]];
    next[idx] = { ...next[idx], [key]: val };
    setP({ ...p, [field]: next });
  }
  function bulletsAsText(arr) { return (arr || []).join("\n"); }
  function textAsBullets(text) { return text.split("\n").map(s => s.trim()).filter(Boolean); }

  return (
    <>
      <h2>Profile</h2>

      {/* Resume auto-fill */}
      <div className="card" style={{ marginBottom: 12 }}>
        <div className="row between">
          <div>
            <strong>Auto-fill from resume PDF</strong>
            <span style={{ color: "var(--muted)", fontSize: 13, marginLeft: 10 }}>
              Claude will extract your info from your PDF and populate the form.
            </span>
          </div>
          <label style={{
            cursor: uploadBusy ? "not-allowed" : "pointer",
            background: "var(--accent)",
            color: "#fff",
            padding: "6px 16px",
            borderRadius: 6,
            fontSize: 13,
            opacity: uploadBusy ? 0.6 : 1,
            whiteSpace: "nowrap",
          }}>
            {uploadBusy ? "Parsing resume…" : "Upload Resume PDF"}
            <input type="file" accept=".pdf" style={{ display: "none" }} disabled={uploadBusy} onChange={handleResumeUpload} />
          </label>
        </div>
        {uploadErr && <div className="banner" style={{ marginTop: 8 }}>{uploadErr}</div>}
      </div>

      <div className="card row between">
        <div className="row">
          <label style={{ margin: 0 }}>Profile</label>
          <select value={currentId || ""} onChange={(e) => load(Number(e.target.value))}>
            <option value="">(new)</option>
            {profiles.map(pr => <option key={pr.id} value={pr.id}>{pr.full_name || `Profile ${pr.id}`}</option>)}
          </select>
          <button className="secondary" onClick={newProfile}>New</button>
          {currentId && <button className="danger" onClick={remove}>Delete</button>}
        </div>
        <div className="row">
          <button onClick={save}>Save</button>
          <span style={{ color: "var(--muted)" }}>{status}</span>
        </div>
      </div>

      <div className="card">
        <div className="grid cols-2">
          <div><label>Full Name</label><input value={p.full_name} onChange={(e) => setField("full_name", e.target.value)} /></div>
          <div><label>Email</label><input value={p.email} onChange={(e) => setField("email", e.target.value)} /></div>
          <div><label>Phone</label><input value={p.phone} onChange={(e) => setField("phone", e.target.value)} /></div>
          <div><label>Location</label><input value={p.location} onChange={(e) => setField("location", e.target.value)} /></div>
          <div><label>LinkedIn</label><input value={p.linkedin} onChange={(e) => setField("linkedin", e.target.value)} /></div>
          <div><label>GitHub</label><input value={p.github} onChange={(e) => setField("github", e.target.value)} /></div>
          <div><label>Website</label><input value={p.website} onChange={(e) => setField("website", e.target.value)} /></div>
        </div>
        <div><label>Default summary (Claude will tailor a new one per job)</label><textarea value={p.summary} onChange={(e) => setField("summary", e.target.value)} /></div>
      </div>

      <Section title="Education" onAdd={() => setField("education", [...p.education, { ...emptyEdu }])}>
        {p.education.map((ed, i) => (
          <div key={i} className="card">
            <div className="grid cols-2">
              <div><label>School</label><input value={ed.school} onChange={(e) => arrField("education", i, "school", e.target.value)} /></div>
              <div><label>Degree</label><input value={ed.degree} onChange={(e) => arrField("education", i, "degree", e.target.value)} /></div>
              <div><label>Location</label><input value={ed.location} onChange={(e) => arrField("education", i, "location", e.target.value)} /></div>
              <div><label>GPA</label><input value={ed.gpa} onChange={(e) => arrField("education", i, "gpa", e.target.value)} /></div>
              <div><label>Start</label><input value={ed.start} onChange={(e) => arrField("education", i, "start", e.target.value)} /></div>
              <div><label>End</label><input value={ed.end} onChange={(e) => arrField("education", i, "end", e.target.value)} /></div>
            </div>
            <div><label>Relevant coursework</label><input value={ed.coursework} onChange={(e) => arrField("education", i, "coursework", e.target.value)} /></div>
            <div><label>Honors</label><input value={ed.honors} onChange={(e) => arrField("education", i, "honors", e.target.value)} /></div>
            <div className="row" style={{ justifyContent: "flex-end" }}>
              <button className="danger" onClick={() => setField("education", p.education.filter((_, j) => j !== i))}>Remove</button>
            </div>
          </div>
        ))}
      </Section>

      <Section title="Work history" onAdd={() => setField("work_history", [...p.work_history, { ...emptyWork }])}>
        {p.work_history.map((w, i) => (
          <div key={i} className="card">
            <div className="grid cols-2">
              <div><label>Title</label><input value={w.title} onChange={(e) => arrField("work_history", i, "title", e.target.value)} /></div>
              <div><label>Company</label><input value={w.company} onChange={(e) => arrField("work_history", i, "company", e.target.value)} /></div>
              <div><label>Location</label><input value={w.location} onChange={(e) => arrField("work_history", i, "location", e.target.value)} /></div>
              <div><label>Start</label><input value={w.start} onChange={(e) => arrField("work_history", i, "start", e.target.value)} /></div>
              <div><label>End</label><input value={w.end} onChange={(e) => arrField("work_history", i, "end", e.target.value)} /></div>
              <div><label>Hours/week (federal)</label><input value={w.hours_per_week} onChange={(e) => arrField("work_history", i, "hours_per_week", e.target.value)} /></div>
              <div><label>Salary (federal)</label><input value={w.salary} onChange={(e) => arrField("work_history", i, "salary", e.target.value)} /></div>
              <div><label>Supervisor (federal)</label><input value={w.supervisor} onChange={(e) => arrField("work_history", i, "supervisor", e.target.value)} /></div>
            </div>
            <div>
              <label>Baseline bullets — one per line. AI will rewrite these per job.</label>
              <textarea value={bulletsAsText(w.bullets)} onChange={(e) => arrField("work_history", i, "bullets", textAsBullets(e.target.value))} />
            </div>
            <div className="row" style={{ justifyContent: "flex-end" }}>
              <button className="danger" onClick={() => setField("work_history", p.work_history.filter((_, j) => j !== i))}>Remove</button>
            </div>
          </div>
        ))}
      </Section>

      <Section title="Projects" onAdd={() => setField("projects", [...p.projects, { ...emptyProject }])}>
        {p.projects.map((pr, i) => (
          <div key={i} className="card">
            <div className="grid cols-2">
              <div><label>Name</label><input value={pr.name} onChange={(e) => arrField("projects", i, "name", e.target.value)} /></div>
              <div><label>Focus</label><input value={pr.focus} onChange={(e) => arrField("projects", i, "focus", e.target.value)} /></div>
              <div><label>Date</label><input value={pr.date} onChange={(e) => arrField("projects", i, "date", e.target.value)} /></div>
            </div>
            <div>
              <label>Bullets — one per line</label>
              <textarea value={bulletsAsText(pr.bullets)} onChange={(e) => arrField("projects", i, "bullets", textAsBullets(e.target.value))} />
            </div>
            <div className="row" style={{ justifyContent: "flex-end" }}>
              <button className="danger" onClick={() => setField("projects", p.projects.filter((_, j) => j !== i))}>Remove</button>
            </div>
          </div>
        ))}
      </Section>

      <Section title="Skills (category → comma-separated values)" onAdd={() => setSkillsRows([...skillsRows, { k: "", v: "" }])}>
        <div className="card">
          {skillsRows.map((row, i) => (
            <div className="row" key={i} style={{ marginBottom: 6 }}>
              <input placeholder="Category (e.g. Languages)" value={row.k} onChange={(e) => { const next = [...skillsRows]; next[i] = { ...row, k: e.target.value }; setSkillsRows(next); }} />
              <input placeholder="Python, TypeScript, Go" value={row.v} onChange={(e) => { const next = [...skillsRows]; next[i] = { ...row, v: e.target.value }; setSkillsRows(next); }} />
              <button className="danger" onClick={() => setSkillsRows(skillsRows.filter((_, j) => j !== i))}>X</button>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Certifications" onAdd={() => setField("certifications", [...p.certifications, ""])}>
        <div className="card">
          {p.certifications.map((c, i) => (
            <div className="row" key={i} style={{ marginBottom: 6 }}>
              <input value={c} onChange={(e) => { const next = [...p.certifications]; next[i] = e.target.value; setField("certifications", next); }} />
              <button className="danger" onClick={() => setField("certifications", p.certifications.filter((_, j) => j !== i))}>X</button>
            </div>
          ))}
        </div>
      </Section>
    </>
  );
}

function Section({ title, onAdd, children }) {
  return (
    <>
      <div className="row between" style={{ marginTop: 18 }}>
        <h3 style={{ margin: 0 }}>{title}</h3>
        <button className="secondary" onClick={onAdd}>+ Add</button>
      </div>
      {children}
    </>
  );
}
