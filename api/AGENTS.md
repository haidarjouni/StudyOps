# StudyOps Django API Guide

This file applies to `api/`. Read the repository-level `AGENTS.md` as well. It describes the backend **as implemented**; check the relevant code and tests before changing a contract. The repository normally prioritizes frontend work. Only edit backend code when the user's request explicitly includes it.

## Request and data flow

1. `manage.py` loads `config/settings.py`; `config/urls.py` mounts each app's `urls.py`.
2. A URL resolves to a DRF view or viewset. Protected views use `IsAuthenticated`, and their `get_queryset()` limits records to `request.user`.
3. A serializer converts request data to model values, validates fields and relationships, then produces the response shape. Views attach `user=request.user` in `perform_create()`; clients do not choose the owner.
4. Django models and migrations define the PostgreSQL schema. The API uses Django's built-in `auth.User` (there is no custom account model).
5. The separate `assistant/` service reads and writes study data through this HTTP API. After a user approves a draft schedule, its client posts to `/api/study_task/schedule/`.

## Where to look

| Area | Responsibilities |
| --- | --- |
| `config/settings.py`, `config/urls.py` | Installed apps, PostgreSQL, UTC/timezone settings, JWT configuration, authentication class, root routes. |
| `accounts/` | Signup, cookie-based JWT login/refresh/logout, authentication, cookie settings. `accounts/models.py` defines no model. |
| `subject/` | Per-user subjects and their unique codes. |
| `study_task/` | Tasks, filters, and the atomic schedule-creation endpoint. |
| `study_session/` | Sessions, filters, ownership/time/overlap validation. |
| `study_preference/` | One preference record per user, created during signup and retrieved/updated through `me`. |
| `thread/` | Per-user assistant conversation records. Conversation/checkpoint state lives in the assistant service, not this model. |
| Each app's `tests.py` and `migrations/` | Existing behavior checks and schema history; use both when changing behavior or fields. |

## Database relationships and deletion

PostgreSQL is configured in `config/settings.py` from environment variables. `USE_TZ=True` and the Django timezone is `UTC`; `StudyPreference.timezone` stores the user's IANA timezone for planning. Do not read or expose the root `.env` file. Django migrations under each app's `migrations/` are the schema history.

| Model | Key fields and relationships | Deletion/constraint behavior |
| --- | --- | --- |
| Django `auth.User` | Owner of all user data. | Deleting a user cascades to its subjects, tasks, sessions, preference, and threads. |
| `subject.Subject` | `user` FK; `name`, `code`, `semester`; timestamps. | Unique `(user, code)` database constraint. Deleting a subject cascades to its tasks and sessions. |
| `study_task.StudyTask` | `user` and `subject` FKs; title, description, type, status, priority, estimated minutes, due date; timestamps. | Deleting a task sets linked sessions' optional `task` FK to null. |
| `study_session.StudySession` | `user` and `subject` FKs; nullable `task` FK; start/end timestamps, status; timestamps. | Session always has a subject; it may have no task. |
| `study_preference.StudyPreference` | `user` one-to-one FK is also its primary key; timezone, daily study hours, preferred session minutes, buffer minutes; timestamps. | One row per user. Signup creates it with the user. |
| `thread.Thread` | UUID primary key; `user` FK, optional title, timestamps. | Deleting the user cascades to threads. |

Except for `Thread` and the preference's user primary key, model IDs use Django's default `BigAutoField`. Task type is `assignment`, `exam`, `study`, or `other`; task status is `todo`, `in_progress`, `done`, or `cancelled`; priority is `low`, `medium`, or `high`. Session status is `scheduled`, `completed`, or `cancelled`. Use the model `TextChoices` as the source of truth if these change.

## Routes and serialization

Read `config/urls.py` and the app's `urls.py` before adding or calling an endpoint. DRF `DefaultRouter` provides list/create and detail CRUD routes for subjects, tasks, sessions, and threads. Current route prefixes are:

| Prefix | View and important contract |
| --- | --- |
| `/api/accounts/` | `signup/`, `login/`, `token/refresh/`, `logout/` are POST routes. |
| `/auth/` | Djoser routes, including `users/me/`. |
| `/api/subject/` | `SubjectView`; `user`, ID, and timestamps are read-only. |
| `/api/study_task/` | `StudyTaskViewSet`; `user`, ID, and timestamps are read-only. `schedule/` is an additional POST action. |
| `/api/study_session/` | `StudySessionViewSet`; reads nested `subject` and `task`, but writes `subject_id` and optional `task_id`. |
| `/api/study_preference/me` | Retrieve/update the current user's preference. This route has no trailing slash in its URL pattern. |
| `/api/thread/` | `ThreadViewSet`; UUID and timestamps are read-only; owner is assigned in the view. |

`SubjectSerializer` checks for an existing code for the same user, excludes the current row during update, then uppercases the submitted code. The database's `(user, code)` constraint is the final uniqueness guard. `StudyTaskSerializer` verifies that a submitted subject belongs to the requester. `StudySessionSerializer` checks subject and optional task ownership, rejects completed/cancelled tasks, requires a task and session to share a subject, requires `start_at < end_at`, and rejects overlap with the user's non-cancelled sessions. Adjacent sessions are allowed; cancelled sessions are excluded from overlap checks. `StudyPreferenceSerializer` requires the latest study time to be after the earliest.

Task filters support subject, type, status, priority, estimated-minute bounds, and due-date bounds. Session filters support subject, task, status, and start/end bounds. The filter definitions are in each app's `filters.py`; do not invent query parameter names.

## Authentication and ownership

`accounts.authentication.CookieJWTAuthentication` reads `access_token` from a request cookie and validates it through Simple JWT. Login writes HTTP-only `access_token` and `refresh_token` cookies via `accounts/utils.py`; refresh reads the refresh cookie and rotates tokens; logout blacklists the refresh token and clears both cookies. Cookie security flags depend on `DEBUG`. JWT lifetimes and rotation settings are in `config/settings.py`.

Protected resource views explicitly set `permission_classes = [IsAuthenticated]`. Their user-filtered querysets prevent listing or retrieving another user's objects; `perform_create()` sets ownership. Related-object checks belong in serializers too, because a user-scoped parent queryset alone does not prevent linking another user's subject or task. Keep ownership checks on create **and update** paths, including nested/bulk actions. Do not put tokens in response bodies, logs, fixtures, or documentation examples.

The current `SignUpView` spells its permission attribute `permission_classses` (three `s` characters after `class`). That is not DRF's `permission_classes` attribute. Anonymous signup currently works under DRF's default permission behavior; do not copy this spelling into new views. If changing authentication, check the actual permission behavior with tests.

## Schedule creation and assistant handoff

`POST /api/study_task/schedule/` accepts a nonempty `drafts` list. Each item contains a task payload and a nonempty `sessions` list. `ScheduleCreateSerializer` and `ScheduleItemCreateSerializer` validate the nested data: new tasks must start as `todo`, sessions must use the same subject and start as `scheduled`, and callers must not supply a task ID for sessions. The view creates each task and its linked sessions in one `transaction.atomic()` block and returns the created drafts with serialized tasks and sessions.

This endpoint is the persistence boundary for an approved assistant draft. The assistant's Pydantic schemas and `assistant/api_client/client.py` also depend on its request and response shapes. A contract change here requires coordinated review of those consumers; do not edit `assistant/` unless the user has authorized that scope.

The schedule endpoint validates nested sessions before saving, while its database writes use `StudyTask.objects.create()` and `StudySession.objects.create()` directly. Model-level `save()` does not run DRF serializer validation. Existing overlap checks query already-persisted sessions; they are not a database exclusion constraint or a comprehensive cross-draft overlap check. When changing bulk scheduling, test multiple new sessions/drafts and transaction rollback explicitly.

## Working conventions for backend changes

- Start with the relevant route, view, serializer, model, migration history, and `tests.py`. Keep request/response formats and ownership behavior consistent across CRUD and schedule paths.
- Put persistent fields and database constraints in models plus migrations; put input/relationship checks in serializers; put HTTP permissions, user-scoped querysets, and transaction orchestration in views. Keep the database as the final guard for invariants that must hold outside API requests.
- For new user-owned resources, filter every read/update/delete queryset by the authenticated user and assign ownership server-side. Validate user-owned foreign keys before saving; test cross-user access and updates.
- Use `transaction.atomic()` for multi-row operations that must succeed or fail together. Check how direct ORM writes interact with serializer-only validation.
- Keep timezone-aware datetimes. Treat preference hours as the user's local planning window and API datetimes as timezone-aware instants.
- Add focused `APITestCase` coverage beside the affected app for valid requests, invalid input, unauthenticated access, cross-user access, update behavior, and any rollback or scheduling edge cases.
- For authorized backend changes, run targeted tests while iterating, then `python manage.py test` from `api/` before completion. The Docker Compose API service is the preferred development environment. Report any failing or unavailable check accurately.
- Preserve unrelated code and migrations. Never modify `.env`, generated files, or another service as an incidental backend change.
