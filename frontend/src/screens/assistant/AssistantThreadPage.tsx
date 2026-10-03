import { useEffect, useRef, useState } from "react";
import { Form, useActionData, useLoaderData, useNavigation } from "react-router";
import type { deleteThreadAction } from "./actions";
import type { assistantThreadLoader } from "./loaders";
import { useAssistantChat } from "./hooks";
import { AssistantConversation } from "../../components/AssistantConversation";

export function AssistantThreadPage() {
  const { thread, timezone, subjects } = useLoaderData<typeof assistantThreadLoader>();
  const chat = useAssistantChat(thread.id, timezone);
  const title = thread.title || "New chat";
  const [confirmingThreadId, setConfirmingThreadId] = useState<string | null>(null);
  const confirmingDelete = confirmingThreadId === thread.id;
  const actionData = useActionData<typeof deleteThreadAction>();
  const [dismissedError, setDismissedError] = useState<unknown>(null);
  const navigation = useNavigation();
  const isDeleting = navigation.state === "submitting";
  const deleteError = !isDeleting && actionData !== dismissedError && actionData?.ok === false
    ? actionData.message
    : null;
  const confirmationRef = useRef<HTMLDivElement>(null);
  const errorRef = useRef<HTMLParagraphElement>(null);
  const deleteButtonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    document.title = `${title} | Assistant | StudyOps`;
  }, [title]);

  useEffect(() => {
    if (confirmingDelete) confirmationRef.current?.focus();
  }, [confirmingDelete]);

  useEffect(() => {
    if (deleteError) errorRef.current?.focus();
  }, [deleteError]);

  function handleCancelDelete() {
    setDismissedError(actionData);
    setConfirmingThreadId(null);
    deleteButtonRef.current?.focus();
  }

  function handleOpenDelete() {
    setDismissedError(actionData);
    setConfirmingThreadId(thread.id);
  }

  return (
    <section aria-labelledby="assistant-title" className="flex min-h-[34rem] flex-col overflow-hidden rounded-3xl border border-border bg-surface-card shadow-card lg:min-h-[calc(100svh-5rem)]">
      <header className="flex items-center gap-4 border-b border-border px-5 py-5 sm:px-7">
        <span aria-hidden="true" className="flex size-11 shrink-0 items-center justify-center rounded-2xl bg-sky-subtle text-sky-dark">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="size-6">
            <path d="M5 6.5A3.5 3.5 0 0 1 8.5 3h7A3.5 3.5 0 0 1 19 6.5v7a3.5 3.5 0 0 1-3.5 3.5H10l-5 4v-7.5Z" />
            <path d="M9 10h6M9 13h4" />
          </svg>
        </span>
        <div className="min-w-0 flex-1">
          <p className="text-xs font-extrabold uppercase tracking-brand text-sky-dark">StudyOps Assistant</p>
          <h1 id="assistant-title" className="truncate text-xl font-extrabold text-text-strong sm:text-2xl">{title}</h1>
        </div>
        <button ref={deleteButtonRef} type="button" aria-expanded={confirmingDelete} aria-controls="delete-chat-confirmation" disabled={isDeleting || chat.pending !== null} onClick={handleOpenDelete} className="min-h-11 shrink-0 rounded-xl border border-coral-dark px-3 py-2 text-sm font-bold text-coral-dark transition-colors hover:bg-coral/10 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-coral disabled:opacity-60 motion-reduce:transition-none">
          Delete chat
        </button>
      </header>

      {confirmingDelete ? (
        <div id="delete-chat-confirmation" ref={confirmationRef} tabIndex={-1} role="group" aria-labelledby="delete-chat-title" onKeyDown={(event) => { if (event.key === "Escape" && !isDeleting) handleCancelDelete(); }} className="border-b border-coral/30 bg-coral/10 px-5 py-5 outline-none focus:ring-3 focus:ring-coral/40 sm:px-7">
          <h2 id="delete-chat-title" className="text-lg font-extrabold text-text-strong">Delete this chat?</h2>
          <p className="mt-1 max-w-xl text-sm leading-6 text-text">This removes the chat from your list. Saved study tasks and sessions stay, and assistant conversation data may remain on the server.</p>
          {deleteError ? (
            <p ref={errorRef} tabIndex={-1} role="alert" className="mt-3 rounded-xl border border-coral/40 bg-surface-card px-4 py-3 text-sm font-semibold text-error-dark outline-none focus:ring-3 focus:ring-coral/40">{deleteError}</p>
          ) : null}
          <div className="mt-4 flex flex-wrap gap-3">
            <Form method="post" aria-busy={isDeleting}>
              <input type="hidden" name="intent" value="delete" />
              <button type="submit" disabled={isDeleting} className="min-h-11 rounded-xl bg-coral-dark px-5 py-2.5 text-sm font-bold text-white transition-colors hover:bg-coral focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-coral disabled:opacity-60 motion-reduce:transition-none">
                {isDeleting ? "Deleting…" : "Yes, delete chat"}
              </button>
            </Form>
            <button type="button" disabled={isDeleting} onClick={handleCancelDelete} className="min-h-11 rounded-xl border border-border bg-surface-card px-5 py-2.5 text-sm font-bold text-text-strong transition-colors hover:bg-cream focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-60 motion-reduce:transition-none">Keep chat</button>
          </div>
        </div>
      ) : null}

      <AssistantConversation key={thread.id} chat={chat} subjects={subjects} timezone={timezone} disabled={isDeleting || confirmingDelete} />
    </section>
  );
}
