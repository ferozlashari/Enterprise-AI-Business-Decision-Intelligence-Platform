# Enterprise AI — Frontend

React 19 + Vite + Tailwind SPA for the Enterprise AI Business Decision
Intelligence Platform. See the [root README](../README.md) for full-stack
setup (Docker, backend, database).

## Local development

```bash
npm install
cp .env.example .env   # defaults to http://localhost:8000 for the backend
npm run dev
```

Runs at http://localhost:5173. Requires the backend running at the URL set
in `VITE_API_URL` (see `.env.example`).

## Scripts

| Command | Purpose |
|---|---|
| `npm run dev` | Start the Vite dev server with hot reload |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint across `src/` |

## Structure

Each feature under `src/features/<name>/` contains a page (`<name>.jsx`),
its API layer (`<name>.api.js`), and a `components/` folder of the small
pieces that page renders. See the root README for the full feature list and
API prefix reference.

## Docker

`Dockerfile` here is a multi-stage build: Node builds the static bundle,
then nginx (`nginx.conf`) serves it with SPA-aware routing. Normally built
via the root `docker-compose.yml` rather than standalone.
