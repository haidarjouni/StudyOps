import { data, redirect, type ActionFunctionArgs } from "react-router";
import * as z from "zod";
import { formErrors, isoValue, numberValue, value } from "../../lib/api";
import type { SessionInput } from "../../types/sessions";
import {
  createSession,
  deleteSession,
  getSession,
  updateSession,
} from "./service";
const schema: z.ZodType<SessionInput> = z
  .strictObject({
    subject_id: z.number().int().positive("Choose a subject."),
    task_id: z.number().int().positive().nullable(),
    start_at: z.iso.datetime({ message: "Choose a start time." }),
    end_at: z.iso.datetime({ message: "Choose an end time." }),
    status: z.enum(["scheduled", "completed", "cancelled"]),
  })
  .refine((values) => values.start_at < values.end_at, {
    path: ["end_at"],
    message: "End time must be after start time.",
  });
async function save({ request, params }: ActionFunctionArgs, edit: boolean) {
  const form = await request.formData();
  const parsed = schema.safeParse({
    subject_id: numberValue(form, "subject_id"),
    task_id: value(form, "task_id") ? numberValue(form, "task_id") : null,
    start_at: isoValue(value(form, "start_at")),
    end_at: isoValue(value(form, "end_at")),
    status: value(form, "status"),
  });
  if (!parsed.success)
    return data(
      { ok: false as const, errors: z.flattenError(parsed.error) },
      { status: 400 }
    );
  try {
    let session;
    // if edit
    if (edit) {
      const current = await getSession(params.id!);
      const unchangedClosedTask =
        current.task &&
        ["done", "cancelled"].includes(current.task.task_status) &&
        current.task.id === parsed.data.task_id;
        // if the task is closed and unchanged, we don't allow changing the task_id, so we remove it from the update data
      if (unchangedClosedTask) {
        // also patch so partial update is allowed
        const otherFields: Partial<SessionInput> = { ...parsed.data };
        delete otherFields.task_id;
        session = await updateSession(params.id!, otherFields);
      } 
      
      else
         session = await updateSession(params.id!, parsed.data);
    } 

    else 
        // if create
        session = await createSession(parsed.data);
    return redirect(`/app/study-sessions/${session.id}?saved=1`);
  } catch (error) {
    return data(
      { ok: false as const, errors: formErrors(error) },
      { status: 400 }
    );
  }
}

export const createSessionAction = (args: ActionFunctionArgs) =>
  save(args, false);

export const editSessionAction = (args: ActionFunctionArgs) => save(args, true);

export async function deleteSessionAction({ params }: ActionFunctionArgs) {
  await deleteSession(params.id!);
  return redirect("/app/study-sessions?deleted=1");
}
