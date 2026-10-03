import { data, redirect, type ActionFunctionArgs } from "react-router";
import { ApiError, formErrors, value } from "../../lib/api";
import { isThreadId } from "./helpers";
import { createThread, deleteThread, sendAssistantMessage } from "./service";
import { assistantInputSchema } from "./schemas";
import type { AssistantInput } from "../../types/assistant";

// Chat is a live interaction; its domain hook owns pending state independently
// of route navigation and delegates all requests to this action/service boundary.
export async function submitAssistantMessage(input: AssistantInput) {
  const parsed = assistantInputSchema.safeParse(input);
  if (!parsed.success) throw new ApiError(400, null);
  return sendAssistantMessage(parsed.data);
}

export async function createThreadAction() {
  try {
    // creates the thread and returns the new thread id, which is used to redirect to the new thread page
    const thread = await createThread();
    return redirect(`/app/assistant/${thread.id}`);
  } catch (error) {
    return data(
      {
        ok: false as const,
        message: formErrors(error).formErrors[0] ?? "Could not create a chat. Try again.",
      },
      { status: 400 },
    );
  }
}

export async function deleteThreadAction({ request, params }: ActionFunctionArgs) {
    // gets teh data from params
  const form = await request.formData();
//   if is to not delete, return error
  if (value(form, "intent") !== "delete") {
    return data({ ok: false as const, message: "Choose a valid action." }, { status: 400 });
  }
// check if it is a thread_id
  if (!isThreadId(params.thread_id)) throw data(null, { status: 404 });

  try {
// deteles the thread and returns to the main page with a query param to show a message
    await deleteThread(params.thread_id);
    return redirect("/app?chat_deleted=1");
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) throw redirect("/login");
    const message = error instanceof ApiError && error.status === 404
      ? "This chat is no longer available. Return to the overview."
      : formErrors(error).formErrors[0] ?? "Could not delete this chat. Try again.";
    const status = error instanceof ApiError
      ? error.status === 0 ? 503 : error.status
      : 500;
    return data({ ok: false as const, message }, { status });
  }
}
