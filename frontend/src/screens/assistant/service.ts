import { ApiError, apiRequest } from "../../lib/api";
import type { AssistantInput, AssistantResponse, Thread } from "../../types/assistant";
import { assistantResponseSchema } from "./schemas";

export const listThreads = () => apiRequest<Thread[]>("/api/thread/");

export const createThread = () =>
  apiRequest<Thread>("/api/thread/", "POST", {});

export const deleteThread = (id: string) =>
  apiRequest<void>(`/api/thread/${encodeURIComponent(id)}/`, "DELETE");

export async function sendAssistantMessage(input: AssistantInput): Promise<AssistantResponse> {
    // verify the thread exists before sending the message to the assistant API
  await apiRequest<Thread>(`/api/thread/${encodeURIComponent(input.thread_id)}/`);
  let response: Response;
//   sends the message to the assistant API and returns the response
  try {
    response = await fetch("/assistant-api/chat", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
  } catch {
    throw new ApiError(0, null);
  }

  // A POST may already have saved a schedule; never retry automatically.
  if (!response.ok) throw new ApiError(response.status, null);
  const result = assistantResponseSchema.safeParse(await response.json().catch(() => null));
  
  if (!result.success) throw new ApiError(502, null);
  return result.data;
}
