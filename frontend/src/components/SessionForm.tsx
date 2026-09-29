import { useEffect, useRef, useState } from "react";
import { Form, Link, useActionData, useNavigation } from "react-router";
import { card, input, primary, secondary } from "./DashboardParts";
import { localValue } from "../lib/api";
import type { Subject } from "../types/subjects";
import type { Task } from "../types/tasks";
import type { StudySession } from "../types/sessions";
import type { createSessionAction } from "../screens/study-sessions/actions";
export function SessionForm({
  session,
  subjects,
  tasks,
}: {
  session: StudySession | null;
  subjects: Subject[];
  tasks: Task[];
}) {
  const [subjectId, setSubjectId] = useState(String(session?.subject.id ?? ""));
  const result = useActionData<typeof createSessionAction>();
  const errors = result?.ok === false ? result.errors : undefined;
  const fieldErrors = errors?.fieldErrors as
    | Record<string, string[]>
    | undefined;
  const busy = useNavigation().state === "submitting";
  const formRef = useRef<HTMLFormElement>(null);
  useEffect(() => {
    if (errors)
      formRef.current
        ?.querySelector<HTMLElement>(
          '[aria-invalid="true"], [data-error-summary]'
        )
        ?.focus();
  }, [errors]);
//   attrs of an inpute field
  const attrs = (name: string) => ({
    id: name,
    name,
    className: input,
    "aria-invalid": !!fieldErrors?.[name],
    "aria-describedby": fieldErrors?.[name] ? `${name}-error` : undefined,
  });
//   an example of a field with a label and an input
  const field = (name: string, label: string, control: React.ReactNode) => (
    <div>
      <label htmlFor={name} className="mb-2 block text-sm font-bold">
        {label}
      </label>
      {control}
      {fieldErrors?.[name]?.[0] ? (
        <p id={`${name}-error`} className="mt-1 text-sm text-error-dark">
          {fieldErrors[name][0]}
        </p>
      ) : null}
    </div>
  );
  const availableTasks = tasks.filter(
    (task) =>
      String(task.subject) === subjectId &&
      ((task.task_status !== "done" && task.task_status !== "cancelled") ||
        task.id === session?.task?.id)
  );
  return (
    <Form
      method="post"
      ref={formRef}
      noValidate
      aria-busy={busy}
      className={`${card} max-w-3xl space-y-5`}
    >
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
        "subject_id",
        "Subject",
        // where control is a select input with the subjects as options
        <select
          {...attrs("subject_id")}
          required
          value={subjectId}
          onChange={(event) => setSubjectId(event.target.value)}
        >
          <option value="">Choose a subject</option>
          {subjects.map((subject) => (
            <option key={subject.id} value={subject.id}>
              {subject.code} · {subject.name}
            </option>
          ))}
        </select>
      )}
      {field(
        "task_id",
        "Related task (optional)",
        <select
          {...attrs("task_id")}
          key={subjectId}
          defaultValue={
            session?.task && String(session.task.subject) === subjectId
              ? session.task.id
              : ""
          }
        >
          <option value="">No linked task</option>
          {availableTasks.map((task) => (
            <option key={task.id} value={task.id}>
              {task.title}
              {task.task_status === "done" || task.task_status === "cancelled"
                ? " (existing link)"
                : ""}
            </option>
          ))}
        </select>
      )}
      <div className="grid gap-5 sm:grid-cols-2">
        {field(
          "start_at",
          "Start date and time",
          <input
            {...attrs("start_at")}
            type="datetime-local"
            required
            defaultValue={session ? localValue(session.start_at) : ""}
          />
        )}
        {field(
          "end_at",
          "End date and time",
          <input
            {...attrs("end_at")}
            type="datetime-local"
            required
            defaultValue={session ? localValue(session.end_at) : ""}
          />
        )}
      </div>
      {field(
        "status",
        "Status",
        <select
          {...attrs("status")}
          defaultValue={session?.status ?? "scheduled"}
        >
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
      )}
      <div className="flex flex-wrap gap-3 pt-2">
        <button type="submit" disabled={busy} className={primary}>
          {busy ? "Saving…" : session ? "Save changes" : "Create session"}
        </button>
        <Link
          to={
            session
              ? `/app/study-sessions/${session.id}`
              : "/app/study-sessions"
          }
          className={secondary}
        >
          Cancel
        </Link>
      </div>
    </Form>
  );
}
