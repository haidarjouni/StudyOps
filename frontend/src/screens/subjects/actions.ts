import { data, redirect, type ActionFunctionArgs } from "react-router";
import * as z from "zod";
import { formErrors, numberValue, value } from "../../lib/api";
import type { SubjectInput } from "../../types/subjects";
import { createSubject, deleteSubject, updateSubject } from "./service";

const schema: z.ZodType<SubjectInput> = z.strictObject({
  name: z.string().min(1, "Enter a name.").max(100),
  code: z.string().min(1, "Enter a code.").max(10),
  semester: z.number().int().positive("Enter a positive semester."),
});

async function save({ request, params }: ActionFunctionArgs, edit: boolean) {
  const form = await request.formData();
  const parsed = schema.safeParse({
    name: value(form, "name"),
    code: value(form, "code").toUpperCase(),
    semester: numberValue(form, "semester"),
  });
  if (!parsed.success)
    return data(
      { ok: false as const, errors: z.flattenError(parsed.error) },
      { status: 400 }
    );
  try {
    const subject = edit
      ? await updateSubject(params.id!, parsed.data)
      : await createSubject(parsed.data);
    return redirect(`/app/subjects/${subject.id}?saved=1`);
  } catch (error) {
    return data(
      { ok: false as const, errors: formErrors(error) },
      { status: 400 }
    );
  }
}
export const createSubjectAction = (args: ActionFunctionArgs) =>save(args, false);

export const editSubjectAction = (args: ActionFunctionArgs) => save(args, true);

export async function deleteSubjectAction({ params }: ActionFunctionArgs) {
  await deleteSubject(params.id!);
  return redirect("/app/subjects?deleted=1");
}
