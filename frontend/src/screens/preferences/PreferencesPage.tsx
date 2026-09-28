import { useEffect, useRef } from "react";
import {
  Form,
  useActionData,
  useLoaderData,
  useNavigation,
} from "react-router";
import {
  card,
  input,
  PageHeading,
  primary,
} from "../../components/DashboardParts";
import type { preferencesAction } from "./actions";
import type { preferencesLoader } from "./loaders";
export function PreferencesPage() {
  const { preferences } = useLoaderData<typeof preferencesLoader>();
  const result = useActionData<typeof preferencesAction>();
  const errors = result?.ok === false ? result.errors : undefined;
  const busy = useNavigation().state === "submitting";
  const formRef = useRef<HTMLFormElement>(null);
  useEffect(() => {
    document.title = "Preferences | StudyOps";
  }, []);
  useEffect(() => {
    if (errors)
      formRef.current
        ?.querySelector<HTMLElement>(
          '[aria-invalid="true"], [data-error-summary]'
        )
        ?.focus();
  }, [errors]);
  const field = (
    name: keyof typeof preferences,
    label: string,
    type: string,
    initial: string | number,
    help?: string
  ) => (
    <div>
      <label htmlFor={name} className="mb-2 block text-sm font-bold">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        min={
          type === "number" ? (name === "buffer_minutes" ? 0 : 1) : undefined
        }
        required
        defaultValue={initial}
        className={input}
        aria-invalid={!!errors?.fieldErrors[name]}
        aria-describedby={
          [
            help ? `${name}-help` : "",
            errors?.fieldErrors[name] ? `${name}-error` : "",
          ]
            .filter(Boolean)
            .join(" ") || undefined
        }
      />
      {help && (
        <p id={`${name}-help`} className="mt-1 text-sm text-text-muted">
          {help}
        </p>
      )}
      {errors?.fieldErrors[name]?.[0] && (
        <p id={`${name}-error`} className="mt-1 text-sm text-error-dark">
          {errors.fieldErrors[name][0]}
        </p>
      )}
    </div>
  );
  return (
    <>
      <PageHeading
        title="Study preferences"
        description="Set the hours and pace that work for you."
      />
      <Form
        method="post"
        ref={formRef}
        noValidate
        aria-busy={busy}
        className={`${card} max-w-3xl space-y-5`}
      >
        {result?.ok === true && (
          <p
            role="status"
            className="rounded-xl bg-success-subtle p-4 font-semibold text-success"
          >
            Preferences saved.
          </p>
        )}
        {errors?.formErrors.length ? (
          <div
            data-error-summary
            tabIndex={-1}
            role="alert"
            className="rounded-xl bg-coral/10 p-4 text-error-dark"
          >
            {errors.formErrors.join(" ")}
          </div>
        ) : null}
        {field(
          "timezone",
          "Time zone",
          "text",
          preferences.timezone,
          "Use an IANA name such as Asia/Beirut."
        )}
        <div className="grid gap-5 sm:grid-cols-2">
          {field(
            "earliest_study_time",
            "Earliest study time",
            "time",
            preferences.earliest_study_time.slice(0, 5)
          )}
          {field(
            "latest_study_time",
            "Latest study time",
            "time",
            preferences.latest_study_time.slice(0, 5)
          )}
        </div>
        <div className="grid gap-5 sm:grid-cols-2">
          {field(
            "preferred_session_minutes",
            "Preferred session length (minutes)",
            "number",
            preferences.preferred_session_minutes
          )}
          {field(
            "buffer_minutes",
            "Buffer between sessions (minutes)",
            "number",
            preferences.buffer_minutes
          )}
        </div>
        <button type="submit" disabled={busy} className={primary}>
          {busy ? "Saving…" : "Save preferences"}
        </button>
      </Form>
    </>
  );
}
