# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Enterprise AI platform with a **FastAPI backend** (`/app/`) and **Vue 3 frontend** (`/frontend/`). It supports multi-provider LLM routing (Azure OpenAI, Google Gemini), a modular skill system, document processing (PPTX, DOCX, PDF), and workflows with DAG execution.

## Development Commands

### Backend
```bash
# Start dev server
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/test_skills.py -v

# Database migrations
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # Vite dev server at localhost:5173
npm run build    # Type-check (vue-tsc) then Vite bundle
npm run preview  # Preview production build
```

### Environment Setup
Copy `.env.example` to `.env`. Minimum required:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_platform
EXECUTION_MODE=mock   # or: azure, gemini, on_prem
SECRET_KEY=<generate: python -c "import secrets; print(secrets.token_urlsafe(64))">
```

## Architecture

### Backend (`/app/`)

**Entry point**: `app/main.py` — lifespan handler runs Alembic migrations → `init_db()` → skill loading on startup. CORS is environment-aware (`CLIENT_ORIGIN` env var for prod).

**Request flow**: Frontend axios (JWT in header) → FastAPI route → `Depends(deps.get_current_user)` + `Depends(get_db)` → service/ORM → Pydantic response.

**Routers** (`app/routers/`): 18 routers registered under `/api/v1/`. Key ones: `auth`, `users`, `chat`, `agent`, `skills`, `workflows`, `runs`, `flowchart`, `ppt`, `meeting`, `policy`.

**Services** (`app/services/`):
- `llm_service.py` — provider-agnostic LLM calls; routes to Azure or Gemini based on the active `AIModel.provider` field. Azure reasoning models (o1, o3, o4-mini) use `max_completion_tokens` instead of `max_tokens`.
- `workflow_engine.py` — DAG execution, step chaining
- `agent_service.py` — agent reasoning and tool calling
- `skill_loader.py` — scans `/app/skills/` on startup, parses YAML frontmatter from each skill's `SKILL.md`, upserts into DB

**Models** (`app/models/`): Core entities in `domain.py` (Workflow, Component, RunExecution, AIModel). User/auth in `user.py`. `UsageLog` in `stats.py` tracks tokens and cost per model per user.

**Config** (`app/core/config.py`): Pydantic `Settings` with four `EXECUTION_MODE` values: `mock`, `azure`, `gemini`, `on_prem`. Three `EMAIL_PROVIDER` values: `smtp`, `azure_acs`, `none`.

### Frontend (`/frontend/src/`)

**Entry**: `main.ts` → creates Vue app, registers Pinia, Vue Router, PrimeVue (Aura theme), mounts. `App.vue` restores session from `localStorage` token on load.

**Routing** (`router/index.ts`): Navigation guard fetches `/users/me` to validate token on every route change. Route `meta` flags: `requiresAuth`, `adminOnly`, `requiresPro`.

**State** (`stores/`): `auth.ts` holds token/user; `theme.ts` handles theme switching. Both are Pinia stores. Component-level state uses `ref()` via Composition API.

**API layer** (`api/`): Axios instance with JWT interceptor (`localStorage['token']` injected automatically). Modules per resource: `agent.ts`, `chat.ts`, `skills.ts`, `models.ts`, etc. Base URL is `/api/v1` (Vite proxies to `localhost:8000` in dev).

**UI**: PrimeVue 4.x with Aura theme. Path alias `@` → `src/`. No linter configured.

### Skills System (`/app/skills/`)

Each skill is a directory containing a `SKILL.md` with YAML frontmatter (name, description, version, tags) and optional test fixtures under `tests/`. Skills are loaded into the database on every app startup via `skill_loader.py`. New skills only need the directory + `SKILL.md` to be discovered automatically.

### Tests (`/tests/`)

`conftest.py` provides `db_session` (SQLite in-memory) and `mock_skill` fixtures. Test files: `test_skills.py`, `test_skills_logic.py`, `test_agent.py`, `test_guardrails.py`. Pytest config in `pytest.ini` sets `pythonpath = .`.

## Key Conventions

- All API prefixes are `/api/v1/...` — defined in `app/core/config.py` as `API_V1_STR`.
- Database sessions are injected via `Depends(get_db)`; never construct sessions manually in route handlers.
- LLM calls should go through `llm_service.py`, not call provider SDKs directly, to preserve usage logging and provider routing.
- Vue components use `<script setup>` (Composition API). No Options API.
- Frontend pages live in `src/pages/`, reusable UI in `src/components/`.
