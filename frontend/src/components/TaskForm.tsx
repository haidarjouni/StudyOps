import { useEffect, useRef } from "react";
import { Form, Link, useActionData, useNavigation } from "react-router";
import { card, input, primary, secondary } from "./DashboardParts";
import { localValue } from "../lib/api";
import type { Subject } from "../types/subjects";
import type { Task } from "../types/tasks";
import type { createTaskAction } from "../screens/tasks/actions";

export function TaskForm({
  task,
  subjects,
}: {
  task: Task | null;
  subjects: Subject[];
}) {
  const result = useActionData<typeof createTaskAction>();
  const errors = result?.ok === false ? result.errors : undefined;
  const fieldErrors = errors?.fieldErrors as
    | Record<string, string[]>
    | undefined;
  const navigation = useNavigation();
  const busy = navigation.state === "submitting";
  const formRef = useRef<HTMLFormElement>(null);
  useEffect(() => {
    if (errors)
      formRef.current
        ?.querySelector<HTMLElement>(
          '[aria-invalid="true"], [data-error-summary]'
        )
        ?.focus();
  }, [errors]);
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
  const attrs = (name: string) => ({
    id: name,
    name,
    className: input,
    "aria-invalid": !!fieldErrors?.[name],
    "aria-describedby": fieldErrors?.[name] ? `${name}-error` : undefined,
  });
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
        "subject",
        "Subject",
        <select
          {...attrs("subject")}
          required
          defaultValue={task?.subject ?? ""}
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
        "title",
        "Title",
        <input
          {...attrs("title")}
          required
          maxLength={100}
          defaultValue={task?.title ?? ""}
          placeholder="What needs doing?"
        />
      )}
      {field(
        "description",
        "Description",
        <textarea
          {...attrs("description")}
          required
          rows={4}
          defaultValue={task?.description ?? ""}
          placeholder="Add the details you need to remember."
        />
      )}
      <div className="grid gap-5 sm:grid-cols-2">
        {field(
          "task_type",
          "Type",
          <select
            {...attrs("task_type")}
            defaultValue={task?.task_type ?? "other"}
          >
            {["assignment", "exam", "study", "other"].map((option) => (
              <option key={option} value={option}>
                {option[0].toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        )}
        {field(
          "task_status",
          "Status",
          <select
            {...attrs("task_status")}
            defaultValue={task?.task_status ?? "todo"}
          >
            <option value="todo">To do</option>
            <option value="in_progress">In progress</option>
            <option value="done">Done</option>
            <option value="cancelled">Cancelled</option>
          </select>
        )}
        {field(
          "task_priority",
          "Priority",
          <select
            {...attrs("task_priority")}
            defaultValue={task?.task_priority ?? "medium"}
          >
            {["low", "medium", "high"].map((option) => (
              <option key={option} value={option}>
                {option[0].toUpperCase() + option.slice(1)}
              </option>
            ))}
          </select>
        )}
        {field(
          "estimated_minutes",
          "Estimated minutes",
          <input
            {...attrs("estimated_minutes")}
            type="number"
            min={1}
            required
            defaultValue={task?.estimated_minutes ?? 45}
          />
        )}
        {field(
          "due_date",
          "Due date and time",
          <input
            {...attrs("due_date")}
            type="datetime-local"
            required
            defaultValue={task ? localValue(task.due_date) : ""}
          />
        )}
      </div>
      <div className="flex flex-wrap gap-3 pt-2">
        <button type="submit" disabled={busy} className={primary}>
          {busy ? "Saving…" : task ? "Save changes" : "Create task"}
        </button>
        <Link
          to={task ? `/app/tasks/${task.id}` : "/app/tasks"}
          className={secondary}
        >
          Cancel
        </Link>
      </div>
    </Form>
  );
}
