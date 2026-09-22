# StudyOps API Contract

This document is the frontend-facing contract for the services currently implemented in this repository. It is derived from the Django URL configuration, views, serializers, models, filters, and tests in `api/`, plus the FastAPI request model, response formatter, review payload, and tests in `assistant/`.

Treat the implementation and its tests as the final source of truth if this document becomes stale. When a backend contract changes, update this file in the same change.

## 1. Services and base URLs

### Django REST API

- Local default: `http://localhost:8000`
- Frontend environment variable: `VITE_API_BASE_URL`
- API routes below are relative to that host, for example:
  - `${VITE_API_BASE_URL}/api/subject/`
  - `${VITE_API_BASE_URL}/auth/users/me/`

`VITE_API_BASE_URL` is a host-level base URL, not an `/api`-prefixed URL.

### Planning assistant

- Local default: `http://localhost:8001`
- Public endpoint: `POST /chat`
- Interactive development documentation: `http://localhost:8001/docs`

The frontend currently has no configured `VITE_ASSISTANT_BASE_URL`. Do not hardcode the local assistant URL in production UI code. Add an approved environment variable or a same-origin server proxy before integrating it.

### Shared wire-format conventions

- Request and response bodies use JSON unless the successful response has no body.
- Integer database IDs are positive integers.
- Thread IDs are UUID strings.
- Date-time values use ISO 8601 and should include a timezone, normally UTC with a `Z` suffix.
- Study-window times use local wall-clock strings such as `"08:00:00"` and do not contain a UTC offset.
- Timezone names are IANA names such as `"Asia/Beirut"`.
- Collection endpoints currently return plain JSON arrays. Pagination is not configured.
- Django REST Framework field errors normally use an object whose keys match request fields.

## 2. Authentication and browser behavior

The Django API uses JWTs stored in HTTP-only cookies:

| Cookie | Lifetime | JavaScript-readable | Other properties |
| --- | ---: | --- | --- |
| `access_token` | 15 minutes | No | `SameSite=Lax`, path `/`, secure outside debug mode |
| `refresh_token` | 30 days | No | `SameSite=Lax`, path `/`, secure outside debug mode |

Frontend requests that depend on authentication must include cookies, for example by using `credentials: "include"` with `fetch`.

The browser must never attempt to read, copy, log, store, or display these tokens. Do not place them in local storage, session storage, React state, URLs, analytics, screenshots, or error messages.

Most application endpoints require authentication and return `401` when the access cookie is absent, expired, or invalid. A frontend may respond to an expired access token by calling the refresh endpoint and retrying the original request once. Avoid unbounded refresh/retry loops.

### Current browser-integration gap

The repository does not currently configure Django CORS headers and the Vite development server does not currently proxy API requests. Direct requests from `http://localhost:5173` to `http://localhost:8000` therefore do not yet have a complete documented browser cross-origin setup.

Use one approved solution before browser integration:

1. configure an appropriate same-origin development proxy; or
2. add an explicitly reviewed CORS configuration that supports credentialed requests.

Do not work around this by exposing JWTs to JavaScript or disabling browser security.

## 3. Endpoint summary

| Area | Method | Path | Authentication |
| --- | --- | --- | --- |
| Account | `POST` | `/api/accounts/signup/` | No |
| Account | `POST` | `/api/accounts/login/` | No |
| Account | `POST` | `/api/accounts/token/refresh/` | Refresh cookie |
| Account | `POST` | `/api/accounts/logout/` | Refresh cookie |
| Current user | `GET` | `/auth/users/me/` | Yes |
| Subjects | CRUD | `/api/subject/` and `/api/subject/{id}/` | Yes |
| Study tasks | CRUD | `/api/study_task/` and `/api/study_task/{id}/` | Yes |
| Schedule batch | `POST` | `/api/study_task/schedule/` | Yes |
| Study sessions | CRUD | `/api/study_session/` and `/api/study_session/{id}/` | Yes |
| Preferences | `GET`, `PUT`, `PATCH` | `/api/study_preference/me` | Yes |
| Threads | `GET`, `POST` | `/api/thread/` | Yes |
| Planning assistant | `POST` | `/chat` on the assistant service | See assistant gap below |

For standard model-viewset CRUD endpoints:

| Operation | Method | Success |
| --- | --- | --- |
| List | `GET /resource/` | `200`, JSON array |
| Create | `POST /resource/` | `201`, created object |
| Retrieve | `GET /resource/{id}/` | `200`, object |
| Replace | `PUT /resource/{id}/` | `200`, updated object |
| Partially update | `PATCH /resource/{id}/` | `200`, updated object |
| Delete | `DELETE /resource/{id}/` | `204`, no body |

Prefer `PATCH` when changing only part of an existing object.

## 4. Account endpoints

### Sign up

`POST /api/accounts/signup/`

Creates both a Django user and that user's required study-preference record in one transaction.

Request:

```json
{
  "username": "study_student_01",
  "email": "student01@example.com",
  "password": "Orbit!Cedar9274",
  "study_preferences": {
    "timezone": "Asia/Beirut",
    "earliest_study_time": "08:00:00",
    "latest_study_time": "21:30:00",
    "preferred_session_minutes": 45,
    "buffer_minutes": 10
  }
}
```

Rules:

- `username`: required, at most 150 characters, unique.
- `email`: required and must be a valid email address.
- `password`: required and checked with Django's configured password validators.
- `study_preferences`: required; see the preference rules below.
- `earliest_study_time` must be earlier than `latest_study_time`.

Success: `201`. The password is never returned. The serializer exposes the submitted non-password account fields and nested study preferences.

Validation failure: `400`. User and preference creation are atomic, so neither is retained when validation or creation fails.

Use this endpoint for StudyOps registration. Although Djoser exposes generated user-management routes under `/auth/`, those additional routes are not an approved replacement for StudyOps signup because they do not create the required study preferences.

### Log in

`POST /api/accounts/login/`

Request:

```json
{
  "username": "study_student_01",
  "password": "Orbit!Cedar9274"
}
```

Success: `200`, sets both JWT cookies and returns:

```json
{
  "message": "Login successful."
}
```

Invalid credentials: `401`. Tokens are not returned in the JSON body.

### Refresh authentication

`POST /api/accounts/token/refresh/`

Request body: empty JSON object or no meaningful body. The refresh token is read from the HTTP-only `refresh_token` cookie.

Success: `200`, rotates both cookies and returns:

```json
{
  "message": "Token refreshed successfully."
}
```

Failure:

- `400` with `{"error": "Refresh token not found in cookies."}` when the cookie is absent.
- `401` with an `error` string when the refresh token is invalid or expired.

### Log out

`POST /api/accounts/logout/`

The endpoint blacklists the refresh token and clears both cookies.

Success: `200`:

```json
{
  "message": "Logout successful."
}
```

The implementation and tests only establish the success case when a valid refresh cookie is present. Missing, invalid, or already-blacklisted refresh-token behavior is not a stable frontend contract; the UI should still clear its authenticated presentation and handle a logout failure safely.

### Current user

`GET /auth/users/me/`

Success: `200`. The current tests guarantee at least:

```json
{
  "id": 1,
  "username": "study_student_01"
}
```

The endpoint is provided by Djoser rather than a project serializer. Do not make new UI depend on additional fields without confirming the runtime response or adding a project-owned serializer contract.

Anonymous request: `401`.

## 5. Subjects

### Subject representation

```json
{
  "id": 12,
  "user": 4,
  "name": "Computer Science",
  "code": "CS101",
  "semester": 1,
  "created_at": "2026-09-01T09:00:00Z",
  "updated_at": "2026-09-01T09:00:00Z"
}
```

Writable fields:

| Field | Type | Rules |
| --- | --- | --- |
| `name` | string | Required, maximum 100 characters |
| `code` | string | Required, maximum 10 characters, normalized to uppercase, unique per user |
| `semester` | integer | Required, positive |

`id`, `user`, `created_at`, and `updated_at` are read-only.

### Routes

- `GET /api/subject/`
- `POST /api/subject/`
- `GET /api/subject/{id}/`
- `PUT /api/subject/{id}/`
- `PATCH /api/subject/{id}/`
- `DELETE /api/subject/{id}/`

Only the authenticated user's subjects are visible. Accessing another user's subject behaves as not found and returns `404`.

Duplicate subject code validation returns `400` with an error under `code`.

Deleting a subject is destructive: its tasks are deleted, and its study sessions are also deleted through their subject relationship. UI should require clear confirmation before deletion.

## 6. Study tasks

### Study-task representation

```json
{
  "id": 21,
  "user": 4,
  "subject": 12,
  "title": "Study chapter 3",
  "description": "Review algorithms.",
  "task_type": "study",
  "task_status": "todo",
  "task_priority": "medium",
  "estimated_minutes": 60,
  "due_date": "2026-09-15T18:00:00Z",
  "created_at": "2026-09-01T09:00:00Z",
  "updated_at": "2026-09-01T09:00:00Z"
}
```

Writable fields:

| Field | Type | Rules |
| --- | --- | --- |
| `subject` | integer | Required; must identify one of the authenticated user's subjects |
| `title` | string | Required, maximum 100 characters |
| `description` | string | Required, nonblank |
| `task_type` | enum | `assignment`, `exam`, `study`, or `other`; defaults to `other` |
| `task_status` | enum | `todo`, `in_progress`, `done`, or `cancelled`; defaults to `todo` |
| `task_priority` | enum | `low`, `medium`, or `high`; defaults to `medium` |
| `estimated_minutes` | integer | Required, positive |
| `due_date` | ISO 8601 date-time | Required; send a timezone-aware value |

`id`, `user`, `created_at`, and `updated_at` are read-only.

### Routes

- `GET /api/study_task/`
- `POST /api/study_task/`
- `GET /api/study_task/{id}/`
- `PUT /api/study_task/{id}/`
- `PATCH /api/study_task/{id}/`
- `DELETE /api/study_task/{id}/`

Only the authenticated user's tasks are visible. Accessing another user's task returns `404`. Assigning a task to another user's subject returns `400` under `subject`.

Deleting a task does not delete its sessions. Existing sessions linked to it remain and their `task` relationship becomes `null`.

### Task filters

Filters are query parameters on `GET /api/study_task/`:

| Query parameter | Meaning |
| --- | --- |
| `subject={id}` | Exact subject ID |
| `task_type={value}` | Exact task type |
| `task_status={value}` | Exact task status |
| `task_priority={value}` | Exact priority |
| `estimated_minutes__gte={number}` | Minimum estimated minutes |
| `estimated_minutes__lte={number}` | Maximum estimated minutes |
| `due_date__gte={timestamp}` | Deadline at or after timestamp |
| `due_date__lte={timestamp}` | Deadline at or before timestamp |

Multiple filters may be combined.

### Create an approved schedule atomically

`POST /api/study_task/schedule/`

This endpoint creates one or more new tasks and their new sessions in a single database transaction. It is used by the planning assistant after schedule approval.

Request:

```json
{
  "drafts": [
    {
      "task": {
        "subject": 12,
        "title": "Prepare for algorithms exam",
        "description": "Review sorting and graph algorithms.",
        "task_type": "exam",
        "task_status": "todo",
        "task_priority": "high",
        "estimated_minutes": 90,
        "due_date": "2026-09-15T18:00:00Z"
      },
      "sessions": [
        {
          "subject_id": 12,
          "start_at": "2026-09-10T17:00:00Z",
          "end_at": "2026-09-10T18:00:00Z",
          "status": "scheduled"
        }
      ]
    }
  ]
}
```

Rules:

- `drafts` must contain at least one item.
- Every item must have one task and at least one session.
- Every new task must start with `task_status: "todo"`.
- Every new session must start with `status: "scheduled"`.
- Session `subject_id` must match the task's `subject`.
- Do not provide a real `task_id`; the endpoint creates the task and links each session automatically.
- The normal ownership, time-range, and task/subject validations still apply.
- Each proposed session is checked for overlap with sessions that already exist in the database. The endpoint does not independently guarantee that two new sessions inside the same submitted batch do not overlap each other; callers should validate the complete draft before submission.
- Any failure rolls back the entire batch.

Success: `201`:

```json
{
  "drafts": [
    {
      "task": { "id": 21, "user": 4, "subject": 12 },
      "sessions": [
        {
          "id": 31,
          "user": 4,
          "subject": { "id": 12 },
          "task": { "id": 21 }
        }
      ]
    }
  ]
}
```

The abbreviated nested objects above contain their complete standard representations in the real response.

## 7. Study sessions

### Study-session representation

Responses use nested subject and task objects:

```json
{
  "id": 31,
  "user": 4,
  "subject": {
    "id": 12,
    "user": 4,
    "name": "Computer Science",
    "code": "CS101",
    "semester": 1,
    "created_at": "2026-09-01T09:00:00Z",
    "updated_at": "2026-09-01T09:00:00Z"
  },
  "task": {
    "id": 21,
    "user": 4,
    "subject": 12,
    "title": "Study chapter 3",
    "description": "Review algorithms.",
    "task_type": "study",
    "task_status": "todo",
    "task_priority": "medium",
    "estimated_minutes": 60,
    "due_date": "2026-09-15T18:00:00Z",
    "created_at": "2026-09-01T09:00:00Z",
    "updated_at": "2026-09-01T09:00:00Z"
  },
  "start_at": "2026-09-10T18:00:00Z",
  "end_at": "2026-09-10T19:00:00Z",
  "status": "scheduled",
  "created_at": "2026-09-01T09:00:00Z",
  "updated_at": "2026-09-01T09:00:00Z"
}
```

`task` may be `null`.

Requests use ID fields instead of nested objects:

```json
{
  "subject_id": 12,
  "task_id": 21,
  "start_at": "2026-09-10T18:00:00Z",
  "end_at": "2026-09-10T19:00:00Z",
  "status": "scheduled"
}
```

Writable fields:

| Field | Type | Rules |
| --- | --- | --- |
| `subject_id` | integer | Required; must be owned by the authenticated user |
| `task_id` | integer or `null` | Optional; task must be owned by the user and belong to `subject_id` |
| `start_at` | ISO 8601 date-time | Required, timezone-aware |
| `end_at` | ISO 8601 date-time | Required, timezone-aware and later than `start_at` |
| `status` | enum | `scheduled`, `completed`, or `cancelled`; defaults to `scheduled` |

`id`, `user`, nested `subject`, nested `task`, `created_at`, and `updated_at` are read-only.

### Routes

- `GET /api/study_session/`
- `POST /api/study_session/`
- `GET /api/study_session/{id}/`
- `PUT /api/study_session/{id}/`
- `PATCH /api/study_session/{id}/`
- `DELETE /api/study_session/{id}/`

List responses are ordered by `start_at` descending.

Validation rules:

- The subject and optional task must belong to the authenticated user.
- A linked task must belong to the same subject as the session.
- A session cannot be linked to a task whose status is `done` or `cancelled`.
- `end_at` must be later than `start_at`.
- A non-cancelled session cannot overlap another non-cancelled session owned by the same user.
- Adjacent sessions are allowed when one ends exactly when the next starts.
- Cancelled sessions do not block the same time range.
- Send `task_id: null` in a `PATCH` request to remove an existing task link.

### Session filters

Filters are query parameters on `GET /api/study_session/`:

| Query parameter | Meaning |
| --- | --- |
| `subject={id}` | Exact subject ID |
| `task={id}` | Exact task ID |
| `status={value}` | Exact status |
| `start_at__gt={timestamp}` | Starts after timestamp |
| `start_at__gte={timestamp}` | Starts at or after timestamp |
| `start_at__lt={timestamp}` | Starts before timestamp |
| `start_at__lte={timestamp}` | Starts at or before timestamp |
| `end_at__gt={timestamp}` | Ends after timestamp |
| `end_at__gte={timestamp}` | Ends at or after timestamp |
| `end_at__lt={timestamp}` | Ends before timestamp |
| `end_at__lte={timestamp}` | Ends at or before timestamp |

To fetch sessions overlapping a window, use both:

```text
end_at__gt={window_start}&start_at__lt={window_end}
```

## 8. Study preferences

Canonical path: `/api/study_preference/me` without a trailing slash.

### Representation

```json
{
  "timezone": "Asia/Beirut",
  "earliest_study_time": "08:00:00",
  "latest_study_time": "21:30:00",
  "preferred_session_minutes": 45,
  "buffer_minutes": 10
}
```

| Field | Type | Rules |
| --- | --- | --- |
| `timezone` | string | Valid IANA timezone, maximum 64 characters |
| `earliest_study_time` | local time | Required, earlier than `latest_study_time` |
| `latest_study_time` | local time | Required, later than `earliest_study_time` |
| `preferred_session_minutes` | integer | Positive |
| `buffer_minutes` | integer | Non-negative |

Routes:

- `GET /api/study_preference/me`
- `PUT /api/study_preference/me`
- `PATCH /api/study_preference/me`

Success: `200`, returning the complete preference representation.

There is no separate create or delete endpoint. StudyOps signup creates the record. A user created through another mechanism may not have a preference record, and the missing-record behavior is not an established frontend contract.

## 9. Conversation threads

### Thread representation

```json
{
  "id": "de37ed11-e643-462a-8d7e-5359ed216e6c",
  "title": "My study plan",
  "created_at": "2026-09-01T09:00:00Z",
  "updated_at": "2026-09-01T09:00:00Z"
}
```

Routes:

- `GET /api/thread/` lists only the authenticated user's threads.
- `POST /api/thread/` creates a thread for the authenticated user.

Create request:

```json
{
  "title": "My study plan"
}
```

`title` is optional, may be blank, and has a maximum length of 255 characters. `id`, `created_at`, and `updated_at` are read-only.

There are currently no retrieve, update, or delete routes for an individual thread. Create a thread through this endpoint before using its ID with the planning assistant.

## 10. Planning assistant chat

`POST /chat` on the assistant service.

The assistant maintains graph state by `thread_id`. A request must contain exactly one of `user_input` or `command`.

### Start or continue a planning request

```json
{
  "thread_id": "de37ed11-e643-462a-8d7e-5359ed216e6c",
  "user_token": "access-token",
  "refresh_token": "refresh-token",
  "time_zone": "Asia/Beirut",
  "user_input": "Plan my study sessions for tomorrow"
}
```

Rules:

- `thread_id`, `user_token`, and `refresh_token` are required nonblank strings.
- `time_zone` is optional, defaults to `Asia/Beirut`, and must be a valid IANA timezone.
- `user_input` must be nonblank.
- Do not include `command` in the same request.

### Respond to a pending schedule review

Approve:

```json
{
  "thread_id": "de37ed11-e643-462a-8d7e-5359ed216e6c",
  "user_token": "access-token",
  "refresh_token": "refresh-token",
  "time_zone": "Asia/Beirut",
  "command": {
    "action": "approve"
  }
}
```

Request changes:

```json
{
  "thread_id": "de37ed11-e643-462a-8d7e-5359ed216e6c",
  "user_token": "access-token",
  "refresh_token": "refresh-token",
  "time_zone": "Asia/Beirut",
  "command": {
    "action": "edit",
    "feedback": "Move Monday's session to Tuesday"
  }
}
```

Cancel:

```json
{
  "thread_id": "de37ed11-e643-462a-8d7e-5359ed216e6c",
  "user_token": "access-token",
  "refresh_token": "refresh-token",
  "time_zone": "Asia/Beirut",
  "command": {
    "action": "cancel"
  }
}
```

Supported actions are `approve`, `edit`, and `cancel`. An edit requires nonblank `feedback`. A command sent when the thread has no pending review returns `409`.

### Assistant responses

Pending review:

```json
{
  "status": "interrupted",
  "interrupts": [
    {
      "type": "schedule_review",
      "title": "Review your study schedule",
      "draft": {
        "drafts": [
          {
            "task": {
              "draft_task_id": "algorithms_exam",
              "subject": 12,
              "title": "Prepare for algorithms exam",
              "description": "Review sorting and graph algorithms.",
              "task_type": "exam",
              "task_status": "todo",
              "task_priority": "high",
              "estimated_minutes": 90,
              "due_date": "2026-09-15T18:00:00Z"
            },
            "study_sessions": [
              {
                "draft_session_id": "algorithms_exam_session_1",
                "draft_task_id": "algorithms_exam",
                "subject_id": 12,
                "task_id": null,
                "start_at": "2026-09-10T17:00:00Z",
                "end_at": "2026-09-10T18:00:00Z",
                "status": "scheduled"
              }
            ]
          }
        ]
      },
      "options": [
        {
          "value": "approve",
          "label": "Approve schedule",
          "variant": "success",
          "requires_feedback": false
        },
        {
          "value": "edit",
          "label": "Request changes",
          "variant": "secondary",
          "requires_feedback": true,
          "feedback": {
            "label": "What would you like to change?",
            "placeholder": "Move Monday's session to Tuesday...",
            "min_length": 1
          }
        },
        {
          "value": "cancel",
          "label": "Cancel",
          "variant": "danger",
          "requires_feedback": false,
          "requires_confirmation": true,
          "confirmation_message": "Discard this draft schedule?"
        }
      ]
    }
  ]
}
```

Approval completion:

```json
{
  "status": "completed",
  "summary": "Saved your study schedule."
}
```

Cancellation:

```json
{
  "status": "cancelled"
}
```

An edit normally returns another `interrupted` response with a revised draft. Sending new `user_input` while a review is pending returns the existing pending review instead of starting a separate run.

### Current assistant-authentication gap

The `/chat` request requires raw `user_token` and `refresh_token` strings so the assistant can call the Django API. The browser cannot read those tokens because the Django API correctly stores them in HTTP-only cookies. Therefore the frontend cannot safely satisfy the current `/chat` request contract directly.

Do not expose the cookies to JavaScript. Before implementing assistant chat in the browser, introduce an approved secure integration such as a same-origin backend proxy that reads the cookies server-side and forwards the credentials to the assistant, or revise the assistant authentication boundary.

## 11. Error handling

### Django API

Common statuses:

| Status | Meaning |
| ---: | --- |
| `200` | Successful read or update |
| `201` | Successful creation |
| `204` | Successful deletion; no response body |
| `400` | Validation or malformed-request error |
| `401` | Missing, expired, or invalid authentication |
| `404` | Resource does not exist or is owned by another user |
| `405` | Method is not supported for the route |

Typical validation error:

```json
{
  "field_name": [
    "Error message."
  ]
}
```

Object-level validation may use `non_field_errors`, while several custom validators attach errors to a specific field such as `subject`, `task_id`, `start_at`, `end_at`, or `latest_study_time`.

Typical authentication or not-found error:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

Frontend code must not assume all error values are strings. Preserve field association where possible and provide a safe general fallback for unexpected shapes.

### Planning assistant

| Status | Meaning |
| ---: | --- |
| `200` | Completed, cancelled, or paused for review; inspect the response `status` |
| `409` | A review command was sent without a pending review |
| `422` | Request-body validation failed |
| `500` | Unhandled assistant, model, checkpoint, or downstream-service failure |

FastAPI validation errors use a `detail` array. Conflict errors use a string:

```json
{
  "detail": "Cannot resume a thread that has no pending interrupt"
}
```

## 12. Frontend implementation rules derived from this contract

- Always use `VITE_API_BASE_URL` for the Django host.
- Include credentials on authenticated Django requests.
- Never access or persist JWT values in frontend code.
- Use the exact enum values documented here.
- Use `subject` when writing a task, but `subject_id` when writing a session.
- Expect a numeric `subject` ID in task responses, but a nested `subject` object in session responses.
- Expect a nested task object or `null` in session responses.
- Use timezone-aware ISO timestamps for deadlines and sessions.
- Render field-level validation from `400` responses instead of replacing it with a generic error whenever possible.
- Model loading, empty, validation, authentication-expired, server-error, and retry states.
- Treat `404` on an authenticated detail route as either missing or inaccessible; do not reveal another user's resource existence.
- Do not call the assistant directly from browser code until its credential-forwarding gap is resolved.
- Do not invent unlisted endpoints, fields, pagination metadata, ordering guarantees, or assistant response states.
