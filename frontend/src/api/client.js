const base = "";
const API_KEY_STORAGE = "jscc_api_key";

export function getApiKey() {
  try { return localStorage.getItem(API_KEY_STORAGE) || ""; } catch { return ""; }
}
export function setApiKey(v) {
  try { localStorage.setItem(API_KEY_STORAGE, v || ""); } catch {}
}

function authHeaders() {
  const k = getApiKey();
  return k ? { "X-API-Key": k } : {};
}

async function req(path, opts = {}) {
  const res = await fetch(base + path, {
    headers: { "Content-Type": "application/json", ...authHeaders(), ...(opts.headers || {}) },
    ...opts,
  });
  if (res.status === 401) {
    throw new Error("401: API key required or invalid. Set it from the top-right field.");
  }
  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try { msg = JSON.parse(text).detail || text; } catch {}
    throw new Error(`${res.status}: ${msg}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

async function downloadFile(path) {
  const res = await fetch(`/api/generate/file?path=${encodeURIComponent(path)}`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error(`${res.status}: download failed`);
  const blob = await res.blob();
  const cd = res.headers.get("Content-Disposition") || "";
  const m = cd.match(/filename="?([^";]+)"?/);
  const name = m ? m[1] : path.split("/").pop();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

export const api = {
  health: () => req("/api/health"),

  listProfiles: () => req("/api/profiles"),
  getProfile: (id) => req(`/api/profiles/${id}`),
  createProfile: (data) => req("/api/profiles", { method: "POST", body: JSON.stringify(data) }),
  updateProfile: (id, data) => req(`/api/profiles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteProfile: (id) => req(`/api/profiles/${id}`, { method: "DELETE" }),

  listJDs: () => req("/api/jds"),
  getJD: (id) => req(`/api/jds/${id}`),
  createJD: (data) => req("/api/jds", { method: "POST", body: JSON.stringify(data) }),
  deleteJD: (id) => req(`/api/jds/${id}`, { method: "DELETE" }),

  listApps: () => req("/api/applications"),
  getApp: (id) => req(`/api/applications/${id}`),
  createApp: (data) => req("/api/applications", { method: "POST", body: JSON.stringify(data) }),
  updateApp: (id, data) => req(`/api/applications/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteApp: (id) => req(`/api/applications/${id}`, { method: "DELETE" }),
  dashboard: () => req("/api/applications/dashboard/summary"),

  genResume: (data) => req("/api/generate/resume", { method: "POST", body: JSON.stringify(data) }),
  genCover: (data) => req("/api/generate/cover-letter", { method: "POST", body: JSON.stringify(data) }),
  download: downloadFile,
};
