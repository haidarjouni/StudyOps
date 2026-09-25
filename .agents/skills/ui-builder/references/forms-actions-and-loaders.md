# Forms, Actions, and Loaders

Use this reference for forms, validation, submissions, loaders, actions, and
fetchers in the StudyOps frontend. StudyOps currently uses React Router Data
Mode through `createBrowserRouter`; verify that mode before applying these
patterns.

Before implementation, read the installed, mode-compatible React Router docs:

```txt
react-router/docs/start/data/actions.md
react-router/docs/start/data/data-loading.md
react-router/docs/start/data/pending-ui.md
react-router/docs/how-to/form-validation.md
react-router/docs/how-to/fetchers.md
react-router/docs/explanation/form-vs-fetcher.md
```

Verify each document's `[MODES: ...]` marker includes Data Mode. Check that
`zod` is installed before using the validation examples. If it is absent, do
not add it unless the current task authorizes that dependency change.

## Responsibilities

Keep each layer narrow:

- The component renders named controls, errors, and pending state. It does not
  call the API from a submit handler or a data-fetching effect.
- The loader reads route inputs and calls typed read functions from a service.
- The action reads `FormData`, normalizes it, validates it with Zod, calls a
  typed mutation service, and returns structured data or a redirect.
- The service owns API paths, `VITE_API_BASE_URL` usage, cookie credentials,
  request serialization, response parsing, and API error mapping.
- The API remains the final authority for authentication, permissions, and
  domain rules. Action-level Zod validation does not replace backend validation.

The normal mutation flow is:

```txt
named controls -> FormData -> normalized candidate -> Zod safeParse
               -> typed service input -> API -> redirect or action data
```

## Choose Form or Fetcher

- Use `<Form method="get">` for search and filters that belong in the URL.
- Use `<Form method="post">` when success should navigate, add history, or
  redirect to a created or updated record.
- Use `<fetcher.Form method="post">` when the mutation must remain on the
  current page, such as an inline toggle, row edit, or dismiss action.
- Use `useSubmit` or `fetcher.submit` only when submission is genuinely
  imperative. Prefer the declarative form components for ordinary user forms.
- Use a separate action target when a navigation form must redirect but an
  inline fetcher mutation must return in-place success data. Do not make one
  action guess how it was submitted.

Let successful actions trigger React Router's normal loader revalidation. Add
`shouldRevalidate` only for a measured or documented reason.

## Define Types Before Schemas

Author the application/request type independently, then constrain the schema's
parsed output with `z.ZodType<Type>`. Keep response types separate from form
input types.

```ts
import * as z from "zod";

export type SubjectFormValues = {
  name: string;
  code?: string;
  semester: number;
  topicIds: string[];
  archived: boolean;
};

export const subjectFormSchema: z.ZodType<SubjectFormValues> = z.strictObject({
  name: z.string().trim().min(1, "Name is required"),
  code: z.string().trim().min(1, "Code cannot be empty").optional(),
  semester: z.number().int().min(1, "Choose a valid semester"),
  topicIds: z.array(z.string().min(1)),
  archived: z.boolean(),
});
```

This annotation checks that successful parsing produces `SubjectFormValues`.
The raw `FormData` is still untrusted and must be normalized before parsing.
When a schema transforms input into a materially different output, define
separate raw and parsed types rather than weakening the application type.

Use `safeParse` for normal form validation. Use `safeParseAsync` only when the
schema actually contains asynchronous checks. Keep checks that require the API
or database in the service/backend flow instead of hiding network calls inside
the schema.

## Normalize FormData Explicitly

Do not pass `Object.fromEntries(formData)` directly to a schema. It discards
repeated values and does not distinguish strings from `File` objects. Normalize
each field according to its intended type:

```ts
function requiredString(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value.trim() : "";
}

function optionalString(formData: FormData, name: string): string | undefined {
  const value = requiredString(formData, name);
  return value === "" ? undefined : value;
}

function numberValue(formData: FormData, name: string): number {
  const value = requiredString(formData, name);
  return value === "" ? Number.NaN : Number(value);
}

function stringList(formData: FormData, name: string): string[] {
  return formData
    .getAll(name)
    .filter((value): value is string => typeof value === "string")
    .map((value) => value.trim())
    .filter(Boolean);
}

export function subjectFormCandidate(formData: FormData): SubjectFormValues {
  return {
    name: requiredString(formData, "name"),
    code: optionalString(formData, "code"),
    semester: numberValue(formData, "semester"),
    topicIds: stringList(formData, "topicIds"),
    archived: formData.get("archived") === "on",
  };
}
```

Handle file inputs explicitly as `File` values and use multipart transport in
the service when the API requires it. Never return passwords, tokens, or other
secrets in action data merely to repopulate a form.

## Standard Validation Failure

Use one discriminated result shape so components can distinguish validation
failure from success without inspecting arbitrary properties:

```ts
export type ValidationFailure<Field extends string = string> = {
  ok: false;
  errors: {
    formErrors: string[];
    fieldErrors: Partial<Record<Field, string[]>>;
  };
};
```

Build the concrete result from Zod's `flattenError`. Return it with status 400;
React Router will not perform normal action revalidation for the failed
submission.

```ts
const parsed = subjectFormSchema.safeParse(candidate);

if (!parsed.success) {
  return data(
    {
      ok: false as const,
      errors: z.flattenError(parsed.error),
    },
    { status: 400 },
  );
}
```

Map backend field validation to the same shape only when the backend contract
provides reliable field names. Put permission, conflict, or cross-field messages
in `formErrors`. Do not expose internal exception text.

## Keep Loaders Thin

Loaders may parse `params` and `request.url`, but services perform the API call.
Parallelize independent reads. Return typed data for expected results; throw a
route response or a mapped service error for an `ErrorBoundary` when the route
cannot render meaningfully.

```ts
import type { LoaderFunctionArgs } from "react-router";
import { listSubjects } from "../services/subjects";

export async function subjectsLoader({ request }: LoaderFunctionArgs) {
  const url = new URL(request.url);
  const query = url.searchParams.get("q")?.trim() || undefined;

  return {
    subjects: await listSubjects({ query }),
  };
}
```

Consume the result with `useLoaderData<typeof subjectsLoader>()`. If StudyOps
later changes router mode, replace this typing pattern with the mode-compatible
approach from the installed React Router docs.

Route-critical reads belong in loaders, not `useEffect`. Component-local reads
that do not define navigation state may use a fetcher when appropriate.

## Keep Actions Thin

Actions select an intent, normalize and validate its payload, call a service,
and choose the route outcome. The service accepts only validated application
types and serializes them for the established API contract.

```ts
import * as z from "zod";
import {
  data,
  redirect,
  type ActionFunctionArgs,
} from "react-router";
import { createSubject } from "../services/subjects";

export async function createSubjectAction({ request }: ActionFunctionArgs) {
  const formData = await request.formData();
  const candidate = subjectFormCandidate(formData);
  const parsed = subjectFormSchema.safeParse(candidate);

  if (!parsed.success) {
    return data(
      {
        ok: false as const,
        errors: z.flattenError(parsed.error),
      },
      { status: 400 },
    );
  }

  const subject = await createSubject(parsed.data);
  return redirect(`/subjects/${subject.id}`);
}
```

The route URL above is illustrative; use the repository's real route and API
contracts. Never invent endpoint paths, request fields, or response fields.

For multiple submit buttons, submit an explicit intent and validate each
intent's own payload:

```tsx
<button type="submit" name="intent" value="save">Save</button>
<button type="submit" name="intent" value="delete">Delete</button>
```

Reject an unknown or missing intent with a 400 response. Do not run a default
mutation for unrecognized input.

For an inline fetcher action, return in-place success data instead of a redirect:

```ts
return data({ ok: true as const, subject });
```

The component reads this from `fetcher.data`; React Router still revalidates
matched loader data after a successful action.

## Render Errors and Pending State Accessibly

In Data Mode, consume route action data with `useActionData<typeof action>()`
and submission state with `useNavigation()`. A fetcher form uses its own
`fetcher.data` and `fetcher.state` so unrelated navigation does not disable it.

```tsx
const actionData = useActionData<typeof createSubjectAction>();
const navigation = useNavigation();
const isSubmitting = navigation.state === "submitting";
const nameErrors = actionData?.ok === false
  ? actionData.errors.fieldErrors.name
  : undefined;

<Form method="post" aria-busy={isSubmitting}>
  <label htmlFor="subject-name">Name</label>
  <input
    id="subject-name"
    name="name"
    aria-invalid={nameErrors?.length ? true : undefined}
    aria-describedby={nameErrors?.length ? "subject-name-error" : undefined}
    required
  />
  {nameErrors?.length ? (
    <p id="subject-name-error" role="alert">{nameErrors[0]}</p>
  ) : null}
  <button type="submit" disabled={isSubmitting}>
    {isSubmitting ? "Saving..." : "Save"}
  </button>
</Form>
```

- Keep native constraints such as `required`, input types, and ranges for quick
  feedback, but treat action validation as authoritative for the frontend.
- Associate every error with its control using `aria-describedby` and set
  `aria-invalid` only when invalid.
- Put form-level errors in a visible `role="alert"` region.
- After a failed submission, focus the first invalid control or a focusable
  form-error summary. A small effect for focus management is acceptable; an
  effect for route data fetching is not.
- Disable only the controls affected by the active submission. Preserve visible
  feedback until the user can understand the outcome.
- Derive optimistic UI only from `navigation.formData` or `fetcher.formData`,
  and reconcile it with loader data after revalidation.

## Service Boundary and Failures

Service functions must:

- derive the base URL from `VITE_API_BASE_URL` through the project's central API
  client or configuration;
- preserve the established cookie-authentication behavior, including credentials
  settings, without exposing tokens to components or logs;
- send the validated payload using the API's actual encoding and field names;
- parse successful responses into declared response types; and
- map non-success responses into a stable project error type.

Actions may convert expected validation or conflict failures into structured
form errors. Loaders/actions should throw unexpected network, authentication,
permission, or server failures to the appropriate route `ErrorBoundary`, unless
the existing auth flow requires a documented redirect. Never silently convert a
failed API request into an empty success state.

## Review Checklist

- The app is still in Data Mode and the installed, mode-compatible docs were read.
- Every successful control has a stable `name`; labels and errors are associated.
- Form choice matches navigation intent: URL form, navigation form, or fetcher.
- `FormData` is normalized explicitly, including repeated and optional values.
- A separately declared TypeScript type constrains the Zod schema output.
- Invalid data returns flattened field/form errors with status 400.
- Successful navigation forms redirect; inline fetcher actions return data.
- Loaders/actions call services rather than owning API configuration or parsing.
- Pending, disabled, error, empty, and success states are handled.
- Route failures reach an `ErrorBoundary`; sensitive details are not displayed.
- Service requests preserve cookie authentication and the configured API base URL.
