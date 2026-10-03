import { useRef, useState } from "react";
import { ApiError } from "../../lib/api";
import type { AssistantCommand, AssistantInput, ChatMessage, ScheduleReview } from "../../types/assistant";
import { submitAssistantMessage } from "./actions";

type Conversation = {
  messages: ChatMessage[];
  reviews: ScheduleReview[];
  pending: "send" | "approve" | "edit" | "cancel" | null;
  error: string | null;
};
const empty: Conversation = { messages: [], reviews: [], pending: null, error: null };

export function useAssistantChat(threadId: string, timeZone: string) {
  // Local history stays isolated by thread while navigating between chats.
  const [conversations, setConversations] = useState<Record<string, Conversation>>({});
  const inFlight = useRef(new Set<string>()); // tracks threads with pending requests to avoid duplicate submissions
  const conversation = conversations[threadId] ?? empty;
  
  function update(change: (current: Conversation) => Conversation) {
    setConversations((all) => ({ ...all, [threadId]: change(all[threadId] ?? empty) }));
  }

  /**
   * Submits a message to the assistant.
   * @param input The input to submit.
   * @returns A promise that resolves to true if the message was submitted successfully, false otherwise.
   * runs the submitAssistantMessage function and updates the conversation state based on the result.
   * If the submission is successful, the conversation state is updated with the new messages and reviews.
   * If the submission fails, the conversation state is updated with an error message.
   * The inFlight set is used to track threads with pending requests to avoid duplicate submissions.
   * The update function is used to update the conversation state.
   * The user text and response text are determined based on the input and the result of the submission.
   * The conversation state is updated with the new messages, reviews, pending status, and error message.
   */
  async function submit(input: AssistantInput): Promise<boolean> {
    if (inFlight.current.has(threadId)) return false;
    inFlight.current.add(threadId);
    const intent = input.command?.action ?? "send";
    // updates the conversation state to indicate that a message is pending and clears any previous error
    update((current) => ({ ...current, pending: intent, error: null }));

    try {
    //  submits the message to the assistant and updates the conversation state with the result
      const result = await submitAssistantMessage(input);
      // determines the user text to display based on the input and the intent
      const userText = input.user_input ?? (
        input.command?.action === "edit"? `Requested changes: ${input.command.feedback}`: intent === "approve" ? "Accept schedule" : "Cancel schedule"
      );
    //    checks the result status and determines the response text to display based on the result and the intent
      const responseText = result.status === "completed" ? result.summary || "The assistant finished this request."
        : result.status === "cancelled" ? "Draft cancelled. No tasks or sessions were created from this draft."
        : intent === "edit" ? "Your revised draft is ready to review." : "Your draft is ready to review. Nothing has been created yet.";
    //   updates the conversation state with the new messages, reviews, pending status, and error message
      update((current) => ({
        messages: [...current.messages,
          { id: crypto.randomUUID(), role: "user", text: userText, kind: intent === "send" ? "chat" : "command" },
          { id: crypto.randomUUID(), role: "assistant", text: responseText,
            kind: result.status === "interrupted" ? "command" : result.status === "cancelled" ? "cancelled" : intent === "approve" ? "completed" : "chat" },
        ],
        reviews: result.status === "interrupted" ? result.interrupts : [],
        pending: null,
        error: null,
      }));
      return true;
    } 
    // to update in errors depending on the status of the error, and to provide a user-friendly message for each case.
    catch (error) {
      const status = error instanceof ApiError ? error.status : 0;
      const message = status === 401 ? "Your session expired. Log in again to continue."
        : status === 409 ? "This draft is no longer awaiting review. Check your tasks before sending a new request."
        : status === 404 ? "This chat is no longer available. Open another chat."
        : status === 429 ? "The assistant is already working on this chat. Wait for it to finish before trying again."
        : status === 400 ? "Enter a message or change request between 1 and 8,000 characters."
        : "Could not get a reply from the assistant. Your input has been kept so you can try again.";
      update((current) => ({ ...current, pending: null,
        reviews: status === 409 || status === 404 ? [] : current.reviews,
        error: intent === "approve" && ![400, 401, 404, 409, 429].includes(status)
          ? "We could not confirm the result. Check your tasks and sessions before accepting again; the schedule may already have been saved."
          : message,
      }));
      return false;
    } finally {
        // removes the thread from the inFlight set to allow future submissions for this thread
      inFlight.current.delete(threadId);
    }
  }

  return {
    // returns the destroyed conversation state and the submit function to send messages or commands to the assistant
    ...conversation,
    send: (message: string) => submit({ thread_id: threadId, time_zone: timeZone, user_input: message.trim() }),
    command: (command: AssistantCommand) => submit({ thread_id: threadId, time_zone: timeZone, command }),
  };
}
