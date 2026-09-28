import { useEffect, useRef } from "react";
import { Form, Link, useActionData, useNavigation } from "react-router";
import { card, input, primary, secondary } from "./DashboardParts";
import type { Subject } from "../types/subjects";
import type { createSubjectAction } from "../screens/subjects/actions";

export function SubjectForm({ subject }: { subject?: Subject }) {
  const result = useActionData<typeof createSubjectAction>();
  const errors = result?.ok === false ? result.errors : undefined;
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
  return (
    <Form
      method="post"
      ref={formRef}
      noValidate
      aria-busy={busy}
      className={`${card} max-w-2xl space-y-5`}
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
      {(
        [
          [
            "name",
            "Subject name",
            subject?.name ?? "",
            "e.g. Computer Science",
          ],
          ["code", "Subject code", subject?.code ?? "", "e.g. CS101"],
          ["semester", "Semester", subject?.semester ?? "", "e.g. 1"],
        ] as const
      ).map(([name, label, initial, placeholder]) => (
        <div key={name}>
          <label htmlFor={name} className="mb-2 block text-sm font-bold">
            {label}
          </label>
          <input
            id={name}
            name={name}
            type={name === "semester" ? "number" : "text"}
            min={name === "semester" ? 1 : undefined}
            maxLength={name === "name" ? 100 : name === "code" ? 10 : undefined}
            required
            defaultValue={initial}
            placeholder={placeholder}
            aria-invalid={!!errors?.fieldErrors[name]}
            aria-describedby={
              errors?.fieldErrors[name] ? `${name}-error` : undefined
            }
            className={input}
          />
          {errors?.fieldErrors[name]?.[0] ? (
            <p id={`${name}-error`} className="mt-1 text-sm text-error-dark">
              {errors.fieldErrors[name][0]}
            </p>
          ) : null}
        </div>
      ))}
      <div className="flex flex-wrap gap-3 pt-2">
        <button type="submit" disabled={busy} className={primary}>
          {busy ? "Saving…" : subject ? "Save changes" : "Create subject"}
        </button>
        <Link
          to={subject ? `/app/subjects/${subject.id}` : "/app/subjects"}
          className={secondary}
        >
          Cancel
        </Link>
      </div>
    </Form>
  );
}
