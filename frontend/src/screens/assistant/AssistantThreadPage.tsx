import { useEffect, useRef, useState } from "react";
import { Form, useActionData, useLoaderData, useNavigation } from "react-router";
import type { deleteThreadAction } from "./actions";
import type { assistantThreadLoader } from "./loaders";

export function AssistantThreadPage() {
  const { thread } = useLoaderData<typeof assistantThreadLoader>();
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
        <button ref={deleteButtonRef} type="button" aria-expanded={confirmingDelete} aria-controls="delete-chat-confirmation" disabled={isDeleting} onClick={handleOpenDelete} className="min-h-11 shrink-0 rounded-xl border border-coral-dark px-3 py-2 text-sm font-bold text-coral-dark transition-colors hover:bg-coral/10 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-coral disabled:opacity-60 motion-reduce:transition-none">
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

      <div className="flex flex-1 items-center justify-center bg-sky-subtle/30 px-5 py-12 sm:px-8">
        <div className="max-w-md text-center">
          <div aria-hidden="true" className="mx-auto flex size-16 items-center justify-center rounded-3xl border border-sky/30 bg-surface-card text-sky-dark shadow-subtle">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" className="size-8">
              <path d="M12 3.5 13.8 9l5.7 2-5.7 2-1.8 5.5L10.2 13l-5.7-2 5.7-2L12 3.5Z" />
              <path d="m19 17 .6 1.4L21 19l-1.4.6L19 21l-.6-1.4L17 19l1.4-.6L19 17Z" />
            </svg>
          </div>
          <h2 className="mt-6 text-2xl font-extrabold text-text-strong sm:text-3xl">Your chat is ready</h2>
          <p className="mt-3 leading-7 text-text-muted">This is your space to plan study time and work through what comes next. Messaging will be available here soon.</p>
        </div>
      </div>

      <div className="border-t border-border bg-surface-card p-4 sm:p-6">
        <div className="mx-auto max-w-3xl">
          <label htmlFor="assistant-message" className="sr-only">Message the StudyOps Assistant</label>
          <div className="flex items-end gap-3 rounded-2xl border border-border bg-cream p-3">
            <textarea id="assistant-message" rows={2} disabled placeholder="Messaging is coming soon" className="min-h-14 min-w-0 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-text-muted outline-none placeholder:text-text-muted" />
            <button type="button" disabled className="min-h-11 shrink-0 rounded-xl bg-accent px-5 text-sm font-extrabold text-text-strong opacity-60">Send</button>
          </div>
          <p className="mt-2 text-center text-xs font-medium text-text-muted">Chat messages are not available yet.</p>
        </div>
      </div>
    </section>
  );
}
