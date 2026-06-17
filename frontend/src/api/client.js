const base = "";

async function req(path, opts = {}) {
  const res = await fetch(base + path, {
    headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
    ...opts,
  });
  if (!res.ok) {
    const text = await res.text();
    let msg = text;
    try { msg = JSON.parse(text).detail || text; } catch {}
    throw new Error(`${res.status}: ${msg}`);
  }
  if (res.status === 204) return null;
  return res.json();
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
  fileUrl: (path) => `/api/generate/file?path=${encodeURIComponent(path)}`,
};
