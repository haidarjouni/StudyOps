---
name: ui-builder
description: Build and verify StudyOps UI exclusively inside frontend/. Use for frontend pages, dashboards, components, layouts, styling, responsive behavior, and interactions. Never use for backend or assistant implementation.
---

# StudyOps UI Builder

Use this skill for implementation work in the StudyOps user-facing React application. Keep the backend, assistant, and their contracts fixed and read-only.

## Required context gate

Before implementing anything, read these sources in order:

1. Repository-root `AGENTS.md`.
2. `frontend/AGENTS.md`.
3. The verified API contract at `docs/api-contract.md`.
4. [references/design.md](references/design.md).
5. The existing frontend files relevant to the requested change.

Do not begin implementation if any required source is unavailable or cannot be read. Report exactly what is missing. If the contract and implementation appear inconsistent, stop only the affected work and report the discrepancy instead of guessing.

## Authority and scope

- During an ordinary UI implementation task, write only inside `frontend/`.
- Treat `frontend/AGENTS.md` as authoritative for folder structure, file placement, component architecture, routes, naming conventions, data fetching, state management, styling conventions, coding standards, dependencies, testing, and verification. Do not duplicate or replace those rules here.
- Treat `references/design.md` as the visual source of truth for layout, spacing, colors, typography, visual hierarchy, component appearance, responsive behavior, interaction patterns, and overall product character.
- Design guidance never overrides the API contract, repository instructions, accessibility requirements, or frontend architecture.
- Read backend or assistant code only when necessary to confirm established behavior.

Never modify `api/`, `assistant/`, backend schemas, database models or migrations, `compose.yaml`, `.env`, root repository files, documentation outside `frontend/`, or this skill during an ordinary UI implementation task.

## Contract discipline

Adapt the frontend to the real backend behavior. Never invent endpoints, fields, enum values, response shapes, status codes, permissions, authentication behavior, or unsupported functionality. Preserve the established cookie-based authentication boundary and other constraints documented in `docs/api-contract.md`.

When requested UI depends on backend or assistant behavior that does not exist:

1. Stop only the unsupported portion; continue independent supported work when safe.
2. Clearly report the contract gap and its UI impact.
3. Suggest a backend contract change separately from the frontend work.
4. Never change backend or assistant code while using this skill. If the user authorizes backend work, handle it separately and without the `ui-builder` skill.

Do not disguise a contract gap with invented live data. Use a mock only when the user explicitly requests one and the repository instructions permit it; keep it isolated and label it temporary.

## Definition of done

A UI task is complete only when:

- the requested frontend behavior works with the existing backend contract;
- the implementation complies with `frontend/AGENTS.md` and `references/design.md`;
- relevant loading, empty, error, success, disabled, hover, focus, and responsive states are handled;
- accessibility and keyboard behavior have been checked;
- frontend lint and production build verification have been run;
- the affected UI has been inspected at mobile and desktop widths when browser access is available; and
- all failures and any verification that could not be performed are reported honestly.
