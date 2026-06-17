# Frontend — React + Vite + Nginx

![React 18](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=white)
![Vite 5](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white)
![React Router 6](https://img.shields.io/badge/React_Router-6-CA4245?style=flat-square&logo=reactrouter&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=flat-square&logo=nginx&logoColor=white)

**Built on Node 20 Alpine (multi-stage Docker build)**

A small single-page React app that drives the backend over `/api/*`. It's intentionally library-light: no Redux, no Tailwind, no UI kit — just React Router, plain CSS, and `fetch`.

## Project layout

```
frontend/
├── Dockerfile             # multi-stage: node:20-alpine build → nginx:alpine serve
├── nginx.conf             # serves /usr/share/nginx/html and proxies /api to backend:8000
├── package.json
├── vite.config.js         # dev server proxies /api → http://localhost:8000
├── index.html
└── src/
    ├── main.jsx           # ReactDOM root + BrowserRouter
    ├── App.jsx            # sidebar + ApiKeyBar + <Routes>
    ├── api/
    │   └── client.js      # fetch wrapper, API_KEY storage, blob download helper
    ├── components/
    │   └── ApiKeyBar.jsx  # top connection bar with live status dot
    ├── pages/
    │   ├── Dashboard.jsx          # KPIs + recent activity
    │   ├── Profile.jsx            # editable profile (multi-profile aware)
    │   ├── JDs.jsx                # paste + parse with Claude
    │   ├── Applications.jsx       # tracker table
    │   └── ApplicationDetail.jsx  # per-app generation page
    └── styles/
        └── index.css      # dark-theme design tokens
```

## Pages

| Route | Component | Notes |
| --- | --- | --- |
| `/` | `Dashboard.jsx` | Three KPI cards (total, follow-ups due, active). Status breakdown chips. Recent activity table linking into application detail. |
| `/profile` | `Profile.jsx` | Multi-profile picker. Forms for education, work history (with federal-only fields hidden but available), projects, skills (category → freeform), certifications. Bullets edited as newline-separated text. |
| `/jds` | `JDs.jsx` | Paste raw posting + channel (`private` / `federal` / `state`). On submit, the backend calls Claude and returns structured fields. Shows keywords, must-haves, responsibilities. |
| `/applications` | `Applications.jsx` | Create new application (profile × JD × template). Inline status select, applied/follow-up date pickers. |
| `/applications/:id` | `ApplicationDetail.jsx` | Pick a template, optionally add free-form instructions, *Generate resume* or *Generate cover letter*. Renders the tailored summary, bullets, missing keywords, warnings. Downloads PDF/.tex/.txt through the blob helper. |

## API client conventions

[`src/api/client.js`](src/api/client.js) is the only place that touches `fetch`. It:

- Reads the API key from `localStorage["jscc_api_key"]` and adds it as `X-API-Key`.
- On 401, throws an error with a clear "API key required or invalid" message so the UI can route the user to the bar.
- Exposes `api.download(path)` which fetches the file as a blob with the auth header, then triggers a browser download — this avoids exposing the API key in a URL query string, which would be the only way for an anchor click to carry credentials.
- Surfaces FastAPI's `detail` field on non-2xx responses so backend validation errors are human-readable.

If you add a new endpoint, add it here and use it from pages — never call `fetch` directly from a component.

## Auth UX

The `ApiKeyBar` at the top of every page (see [`src/components/ApiKeyBar.jsx`](src/components/ApiKeyBar.jsx)):

- Hits `GET /api/health` on mount and after every save, then renders one of:
  - **green dot** "connected" — backend reachable, key (if needed) accepted.
  - **amber dot** "needs key" — backend returned 401.
  - **red dot** "backend down" — fetch threw.
- Password-type input so the key doesn't sit visible on screen.
- Persists to localStorage; survives reloads.

## Running locally (without Docker)

You'll need Node 20+ and the backend running on `:8000`.

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173, proxies /api to http://localhost:8000
```

Override the backend URL with `VITE_API_URL`:

```bash
VITE_API_URL=http://my-backend:8000 npm run dev
```

## Build for production

```bash
npm run build        # produces dist/
npm run preview      # serves dist/ on :5173 for a smoke test
```

In Docker, the build stage runs `npm run build` and the serve stage is Nginx with [`nginx.conf`](nginx.conf):

- Static assets served from `/usr/share/nginx/html` with SPA-style `try_files $uri $uri/ /index.html`.
- `/api/` proxied to `http://backend:8000` (the Docker network DNS name from `docker-compose.yml`).
- `proxy_read_timeout 300s` so slow Claude generations don't time out at the proxy.

## Theming

All colors live as CSS custom properties in [`src/styles/index.css`](src/styles/index.css):

```css
--bg, --panel, --panel-2, --border, --text, --muted,
--accent, --accent-2, --danger, --warn
```

Swap them to retheme the app. There's no separate light mode — the current palette is dark by default and easy to read for long-form work.

## Adding a new page

1. Create `src/pages/Foo.jsx` exporting a default React component.
2. Import it in `App.jsx` and add `<Route path="/foo" element={<Foo />} />`.
3. Add a `<NavLink to="/foo">Foo</NavLink>` in the sidebar.
4. If it needs new endpoints, add them to `api/client.js` first.

## What's deliberately *not* here

- No global state library — React local state is enough for an app this size, and the API is the source of truth.
- No form library — every form is a few `useState` calls. If forms grow, swap in React Hook Form.
- No testing framework — the backend has pytest coverage; the frontend is small enough to test by use. Add Vitest + React Testing Library if interactions get complex.
