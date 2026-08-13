# Enterprise AI — Business Decision Intelligence Platform

A full-stack enterprise platform combining ML-driven sales/inventory/customer
prediction, a multi-agent decision engine, a RAG-powered AI Copilot, and a
React dashboard — backed by FastAPI, PostgreSQL, Redis, and Celery.

---

## 1. Architecture

```
frontend/          React 19 + Vite + Tailwind SPA (nginx in production)
backend/            FastAPI application
  ├─ api/           REST routers (sales, inventory, forecast, customer,
  │                  dashboard, decision, recommendation, copilot, reports,
  │                  alerts, cache, tasks, multi-agent chat)
  ├─ auth/           JWT auth, password hashing, route dependencies
  ├─ database/        SQLAlchemy models + session management
  ├─ services/         Business logic behind each API router
  ├─ models/            Trained ML model wrappers (sales/inventory/forecast/
  │                      customer segmentation)
  ├─ copilot/            RAG-aware chat pipeline
  ├─ multi_agent/         LangGraph agent graph (nodes/state/graph)
  ├─ orchestrator/         Agent planning/execution/routing
  ├─ monitoring/            Health + request metrics
  ├─ cache/                  Redis cache helpers
  └─ tasks/                   Celery background jobs
agents/              Standalone LangGraph-style agents (forecast, inventory,
                      decision, executive, report, data, orchestrator)
rag/                  Retrieval pipeline: embeddings, vector store, retriever,
                      document loader, prompt templates
config/               Centralized Pydantic Settings (reads `.env`)
alembic/              Database migrations
dashboards/           Standalone Streamlit business dashboard (optional,
                      separate from the React frontend)
datasets/, knowledge_base/, saved_models/, vector_db/, outputs/, reports/
                      Data the app reads/writes at runtime
```

The React frontend and the FastAPI backend are fully decoupled — the SPA
talks to the API only over HTTP (`VITE_API_URL`), so either can be
redeployed independently.

---

## 2. Quick Start — Docker (recommended)

This brings up PostgreSQL, Redis, the FastAPI backend, a Celery worker, and
the built React frontend (served by nginx) together.

```bash
cp .env.example .env
# edit .env — at minimum set SECRET_KEY and GROQ_API_KEY

docker compose up --build
```

- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000** (interactive docs at `/docs`)
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

The backend, celery worker, and Postgres/Redis containers are networked
together automatically (`docker-compose.yml` overrides `DATABASE_URL`,
`REDIS_URL`, and the Celery URLs to point at the `postgres`/`redis` service
names). The frontend's `VITE_API_URL` is baked in at build time to
`http://localhost:8000`, since the **browser** calls the API directly, not
container-to-container.

Data directories (`datasets/`, `knowledge_base/`, `saved_models/`,
`vector_db/`, `outputs/`, `reports/`, `logs/`) are mounted as volumes rather
than baked into the image, so you can update data without rebuilding.

### Run database migrations (first run only)

```bash
docker compose exec backend alembic upgrade head
```

### Useful Docker commands

```bash
docker compose logs -f backend        # tail backend logs
docker compose exec backend bash      # shell into the backend container
docker compose down                   # stop everything
docker compose down -v                # stop and wipe Postgres/Redis volumes
```

---

## 3. Manual Setup (without Docker)

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16 running locally
- Redis 7 running locally

### Backend

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env
# edit .env — set SECRET_KEY, GROQ_API_KEY, and DB_* to match your local Postgres

alembic upgrade head

uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Celery worker (background jobs — sales prediction reruns, report
generation, RAG re-indexing)

```bash
celery -A backend.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install

cp .env
# VITE_API_URL defaults to http://localhost:8000, which matches the
# backend command above

npm run dev
```

Frontend dev server: **http://localhost:5173**

### Optional — standalone Streamlit dashboard

```bash
streamlit run dashboards/business_dashboard.py
```

This is a separate, self-contained business dashboard — not part of the
React app, and not required for the main platform to work.

---

## 4. Environment Variables

See `.env.example` (root) and `frontend/.env.example` for the full list with
inline explanations. The important ones to change before any real
deployment:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | JWT signing key — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `GROQ_API_KEY` | Powers the AI Copilot / multi-agent chat (Groq LLM) |
| `DATABASE_URL` | PostgreSQL connection string (auto-overridden by Docker Compose) |
| `REDIS_URL` / `CELERY_*` | Redis + Celery broker/backend (auto-overridden by Docker Compose) |
| `FRONTEND_URL` | Must match the origin the browser loads the frontend from — used for CORS |

---

## 5. Database Migrations

Migrations live in `alembic/versions/`. To create a new one after changing
`backend/database/models.py`:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

---

## 6. Frontend Structure

Each feature under `frontend/src/features/<name>/` follows the same
convention:

```
<name>.jsx            Page — fetches data, composes components
<name>.api.js          API calls for this feature
components/             Small presentational components (charts, tables,
                          cards) used by the page
```

Features: `auth`, `dashboard`, `sales`, `inventory`, `forecast`, `customer`,
`decision`, `copilot`, `reports`, `monitoring`, `settings`.

### Known lint note

`AuthContext.jsx` exports both a React context and a provider component from
the same file, which trips the `react-refresh/only-export-components` rule
(a hot-reload nicety, not a runtime bug). Splitting it would require
updating every file that imports `AuthContext`, so it's left as-is
intentionally — flagging it here so it isn't mistaken for an oversight.

---

## 7. Case Study Alignment (Ezitech EEF — AI-002)

How this platform maps to the case study's required modules:

| Case study module | Implementation |
|---|---|
| Enterprise Data Connector | `backend/api/*` ingest from PostgreSQL-backed sales/inventory/customer datasets; extensible per-domain services in `backend/services/` |
| AI Business Analyst | AI Copilot (`/copilot/chat`) + multi-agent chat (`/ai/chat`) answer natural-language business questions grounded in real data |
| Decision Recommendation Engine | `/decision/run` — takes live business metrics, returns risk level, identified risks, and ranked recommendations; full run history at `/decision/` |
| AI Executive Copilot | RAG-aware chat (`rag/` pipeline: embeddings, vector store, retriever) over `knowledge_base/` |
| Explainable AI | Decision engine responses include risk factors and the metrics that drove them (`Decision.jsx` renders these in `RiskCard`/`ImpactChart`, not just a bare verdict) |
| Executive Dashboard | `/dashboard/executive` — revenue, profit, inventory, customer growth, alerts, AI recommendations in one view |
| Alert Center | `/alerts/*` — active alerts with severity, acknowledge/resolve workflow, role-gated actions; live in the Navbar notification bell |
| Forecasting Models | Prophet-based sales/inventory forecasting (`/forecast/*`), rendered as trend charts with confidence bands |
| Multi-Agent AI | `agents/` (forecast, inventory, decision, executive, report, data agents + orchestrator) and `backend/multi_agent/` (LangGraph graph/nodes/state) |
| Knowledge Graph | Relationship modeling via `rag/` document indexing over enterprise knowledge base content; NetworkX available for graph-structured reasoning |
| Reporting | `/reports/*` — sales, inventory, customer, forecast, business KPI, executive, dashboard, and AI-insight reports, each individually viewable and regenerable from the Reports page |

Full-stack settings control (Settings page): account info, **change password** (server-verified against the current password, bcrypt-hashed), background job triggers (rerun sales prediction, regenerate all reports, rebuild the RAG index), and cache administration — all backed by real endpoints, not placeholders.

---

## 8. API Overview

All routes are prefixed as shown; see `http://localhost:8000/docs` for the
full interactive schema once the backend is running.

| Prefix | Covers |
|---|---|
| `/auth` | Register, login, current user, change password (authenticated), forgot/reset password (email-token flow) |
| `/sales` | Sales data, prediction, feature importance, reports |
| `/inventory` | Inventory data + demand prediction |
| `/forecast` | Sales/inventory demand forecasting (Prophet) |
| `/customer` | Customer segmentation + stats |
| `/dashboard` | Executive dashboard aggregation, alerts |
| `/decision` | Decision engine — run, history, recommendations |
| `/recommendation` | Standalone recommendation generation |
| `/copilot` | RAG-aware AI chat |
| `/ai` | Multi-agent chat (business analysis without RAG) |
| `/reports` | Per-domain + executive reports, generated file listing |
| `/alerts` | Business alert rules |
| `/cache` | Redis cache admin (clear) |
| `/tasks` | Trigger Celery background jobs |
| `/monitor` | Health + request metrics |

---

## 9. Production Notes

- The frontend Docker image is a **multi-stage** build (Node build stage →
  nginx runtime stage), so the shipped image contains no `node_modules` or
  source — just the static bundle.
- The backend Docker image installs from `requirements.txt` only; large data
  directories are mounted as volumes, not baked in, to keep rebuilds fast.
- CORS (`backend/main.py`) is driven by `FRONTEND_URL` plus a small set of
  known local dev/preview origins — update `FRONTEND_URL` for any other
  deployment origin.
- Celery reads its broker/backend URLs from `config/settings.py` (via
  `.env`), so worker containers and the API stay in sync automatically.
