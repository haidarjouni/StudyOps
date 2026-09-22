# StudyOps Repository Instructions

## 1. Product Purpose

StudyOps is a personal study-management application. It allows authenticated users to:

- organize subjects by name, code, and semester;
- create and track assignments, exams, study work, and other tasks;
- schedule study sessions linked to subjects and optionally to tasks;
- configure study preferences such as timezone, study hours, preferred session length, and buffer time;
- maintain conversation threads with an AI planning assistant; and
- request, review, edit, approve, or cancel AI-generated study schedules before sessions are created.

The current implementation priority is the user-facing frontend. Treat the existing backend and planning assistant as established services unless the user explicitly asks for changes to them.

## 2. Repository Structure

- `frontend/`: React single-page application. This is the default implementation scope for UI work.
  - `src/`: application components, routes, styles, and assets.
  - `public/`: static public assets.
- `api/`: Django REST Framework service.
  - `accounts/`: signup, login, refresh, and logout using cookie-based JWT authentication.
  - `subject/`: subject CRUD endpoints.
  - `study_task/`: study-task CRUD and filtering.
  - `study_session/`: scheduled-session CRUD and filtering.
  - `study_preference/`: per-user study preferences.
  - `thread/`: assistant conversation-thread creation and listing.
  - `config/`: Django settings and root URL configuration.
- `assistant/`: FastAPI and LangGraph study-planning service.
  - `main.py`: HTTP entry point for `POST /chat`.
  - `agent.py`, `nodes.py`, and `planning.py`: graph workflow and deterministic planning logic.
  - `schemas/`: request, planning, and schedule validation models.
  - `api_client/`: client code for communicating with the Django API.
  - `tests/`: assistant test suite.
- `compose.yaml`: local orchestration for PostgreSQL, API, frontend, and assistant services.
- `.env`: local secrets and environment configuration. Never read, print, commit, or modify it unless the user explicitly requests a specific safe change.
- `output/` and `tmp/`: generated or temporary artifacts; they are not application source.

## 3. Technologies

### Frontend

- React 19
- React Router 8
- Vite 8
- TypeScript and Tailwind CSS 4
- Oxlint
- npm with `package-lock.json`

### Backend API

- Python 3.12
- Django 5.2
- Django REST Framework
- Djoser and Simple JWT
- Cookie-based JWT authentication
- django-filter
- PostgreSQL

### Planning Assistant

- Python 3.12
- FastAPI and Uvicorn
- LangChain and LangGraph
- OpenAI-compatible chat models through `langchain-openai`
- Pydantic schemas
- PostgreSQL-backed LangGraph checkpoints
- pytest

### Local Infrastructure

- Docker Compose
- PostgreSQL 17

## 4. Commands

Run commands from the repository root unless another directory is specified.

### Run the complete application

- Build and start all services: `docker compose up --build`
- Start existing containers: `docker compose up`
- Stop the services: `docker compose down`

Default local service URLs are:

- Frontend: `http://localhost:5173`
- Django API: `http://localhost:8000`
- Assistant: `http://localhost:8001`
- Assistant interactive documentation: `http://localhost:8001/docs`

Host ports may be overridden through environment variables in `compose.yaml`.

### Frontend

Run these inside `frontend/`:

- Install exact locked dependencies: `npm ci`
- Start the development server: `npm run dev`
- Lint: `npm run lint`
- Create a production build: `npm run build`
- Preview a production build: `npm run preview`

### Django API

The Docker Compose service is the preferred development path. For an explicitly requested local API run, use the configured Python environment, install `api/requirements.txt`, then run inside `api/`:

- Apply migrations: `python manage.py migrate`
- Start the server: `python manage.py runserver 0.0.0.0:8000`
- Run tests: `python manage.py test`

### Planning Assistant

The Docker Compose service is the preferred development path. For an explicitly requested local run, install `assistant/requirements.txt`, ensure the API and database are available, then run inside `assistant/`:

- Start the server: `python -m uvicorn main:app --port 8001 --reload`
- Run tests: `python -m pytest`

## 5. Default Modification Scope

For frontend and UI requests, the agent may modify:

- `frontend/src/`
- `frontend/public/`
- frontend configuration files when required for the requested UI behavior;
- `frontend/package.json` and `frontend/package-lock.json` only under the dependency rules below; and
- project documentation or instruction files only when the user asks for documentation changes or when an approved implementation makes an existing instruction factually incorrect.

The agent may read backend and assistant code to understand available behavior and API contracts.

## 6. Protected and Untouched Areas

Unless the user explicitly expands the scope, do not modify:

- `api/`
- `assistant/`
- database models or migrations;
- `compose.yaml`;
- `.env` or other secret-bearing files;
- `.git/`;
- `.venv*`, `node_modules/`, Python caches, build output, coverage output, `output/`, or `tmp/`; or
- generated dependency files outside an explicitly approved dependency change.

Do not delete or rewrite existing application code merely to simplify frontend implementation. Preserve unrelated and user-authored changes.

## 7. Testing and Verification

For every frontend behavior change:

1. Run `npm run lint` inside `frontend/`.
2. Run `npm run build` inside `frontend/`.
3. Start or reuse the application and inspect the affected screen in a browser when browser access is available.
4. Check the affected UI at narrow mobile and desktop widths.
5. Exercise the primary interaction path and inspect the browser console for errors.
6. Verify relevant loading, empty, error, disabled, success, hover, and focus states.
7. Check keyboard accessibility, visible focus, semantic labels, contrast, and obvious overflow issues.

The frontend currently has no automated test command. Do not claim frontend automated tests passed unless a test runner is later added and actually executed.

If the user explicitly authorizes backend changes, run the relevant Django tests with `python manage.py test`. If the user explicitly authorizes assistant changes, run `python -m pytest` inside `assistant/`. Prefer targeted tests during iteration and the complete affected service suite before completion.

Never hide or silently ignore a failing check. Report the exact failure and distinguish pre-existing failures from regressions caused by the current work.

## 8. Dependency Rules

- Use npm for the frontend because the repository includes `package-lock.json`.
- Use `npm ci` for clean installs and reproducible verification.
- Prefer existing dependencies, React APIs, browser APIs, and ordinary CSS before adding packages.
- Ask for confirmation before adding a production dependency, UI framework, CSS framework, state-management library, charting library, icon package, or other substantial dependency.
- Add a development dependency only when it materially improves required validation or implementation and cannot reasonably be avoided.
- Keep `package.json` and `package-lock.json` synchronized. Do not hand-edit the lockfile.
- Do not switch package managers or introduce another lockfile.
- Do not upgrade unrelated packages as part of frontend feature work.
- Do not change Python dependencies unless backend or assistant work was explicitly requested.

## 9. Backend API Contract Rules

- Treat existing Django views, serializers, URL configurations, tests, and assistant request schemas as the source of truth.
- The frontend API base URL must come from `VITE_API_BASE_URL`; do not hardcode deployment-specific hosts.
- Do not invent endpoints, fields, enum values, response shapes, status codes, or authentication behavior.
- Inspect the relevant backend implementation before connecting a frontend feature.
- Preserve the existing cookie-based JWT authentication design. Never expose credentials or tokens in source code, logs, screenshots, fixtures, or user-visible error messages.
- The main Django API namespaces include accounts, subjects, study tasks, study sessions, study preferences, and threads. Use the actual URL configuration rather than guessing endpoint paths.
- The planning assistant is a separate service with `POST /chat`. Its review flow supports approve, cancel, and edit commands and may return interrupted, completed, or cancelled states. Follow its request and response schemas exactly.
- A conversation thread must exist through the Django API before it is used with the assistant.
- Do not alter backend behavior to accommodate a preferred frontend design. Adapt the frontend to the established contract.
- If the desired UI requires unavailable backend data or behavior, isolate any temporary mock behind a clear boundary, label it as temporary, and report the contract gap. Do not silently present invented data as live data.
- Propose backend contract changes separately and wait for explicit approval before editing backend or assistant code.
