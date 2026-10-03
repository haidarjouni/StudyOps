import { useEffect, useRef, useState, type FormEvent } from "react";
import { Link } from "react-router";
import type { useAssistantChat } from "../screens/assistant/hooks";
import type { Subject } from "../types/subjects";
import { AssistantScheduleReview } from "./AssistantScheduleReview";

type AssistantConversationProps = {
  chat: ReturnType<typeof useAssistantChat>; // the chat state and actions for the current thread
  subjects: Subject[]; 
  timezone: string;
  disabled: boolean;
};

const button = "min-h-11 rounded-xl px-5 py-2.5 text-sm font-extrabold transition-colors focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-not-allowed disabled:opacity-60 motion-reduce:transition-none";
const input = "mt-2 w-full resize-y rounded-xl border border-border bg-surface-card px-4 py-3 text-sm leading-6 text-text-strong placeholder:text-text-muted focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-60";

export function AssistantConversation({ chat, subjects, timezone, disabled }: AssistantConversationProps) {
  const [message, setMessage] = useState("");
  const [feedback, setFeedback] = useState("");
  const [confirmCancel, setConfirmCancel] = useState(false);

  const busy = chat.pending !== null; // true if the chat is currently processing a message or command
  const locked = busy || disabled; // true if the chat is busy or disabled, preventing user input
  const reviewing = chat.reviews.length > 0; // true if there are schedule reviews awaiting user action
  const reviewRef = useRef<HTMLElement>(null); // ref to the schedule review section for focus management
  const errorRef = useRef<HTMLDivElement>(null); // ref to the error message section for focus management
  const messageRef = useRef<HTMLTextAreaElement>(null); // ref to the message input textarea for focus management
  const cancelRef = useRef<HTMLButtonElement>(null);// ref to the cancel button for focus management
  const confirmRef = useRef<HTMLDivElement>(null);// ref to the cancel confirmation section for focus management
  const lastReview = useRef(chat.reviews);// ref to the last known reviews for comparison in useEffect
  const endRef = useRef<HTMLDivElement>(null); // ref to the end of the conversation for scrolling into view when new messages are added

  useEffect(() => {
    if (chat.error) errorRef.current?.focus();
  }, [chat.error]);

// checks if the reviews have changed, if so, focus on the review section, otherwise focus on the message input
  useEffect(() => {
    if (chat.reviews === lastReview.current) return;
    lastReview.current = chat.reviews;
    if (chat.reviews.length) reviewRef.current?.focus();
    else messageRef.current?.focus();
  }, [chat.reviews]);
//   scrolls to the bottom of the conversation when a new message is added
  useEffect(() => {
    if (chat.messages.length) endRef.current?.scrollIntoView({ block: "nearest" });
  }, [chat.messages.length]);

//   focuses on the cancel confirmation section when the user clicks the cancel button
  useEffect(() => {
    if (confirmCancel) confirmRef.current?.focus();
  }, [confirmCancel]);
//   focuses on the message input when the user clicks the cancel button
  async function handleSend(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (locked || reviewing || !message.trim()) return;
    if (await chat.send(message)) setMessage("");
  }
//  handles the edit command, submits the feedback to the assistant, and clears the feedback input
  async function handleEdit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (locked || !feedback.trim()) return;
    setConfirmCancel(false);
    if (await chat.command({ action: "edit", feedback: feedback.trim() })) setFeedback("");
  }

  function handleKeepDraft() {
    setConfirmCancel(false);
    cancelRef.current?.focus();
  }

  return (
    <>
      <div className="flex-1 bg-sky-subtle/30 px-4 py-6 sm:px-7">
        <div className="mx-auto max-w-3xl space-y-5">
          {chat.messages.length === 0 && !busy ? (
            <div className="px-2 py-12 text-center">
              <p className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">Let's make a plan</p>
              <h2 className="mt-3 text-2xl font-extrabold text-text-strong sm:text-3xl">What are you working on?</h2>
              <p className="mx-auto mt-3 max-w-md leading-7 text-text-muted">Tell me what you need to study and when it is due. You can review, change, or cancel a proposed schedule before anything is created.</p>
              <p className="mx-auto mt-4 max-w-md text-xs leading-5 text-text-muted">Earlier messages are not loaded when you reopen a chat. If a draft is pending, your next message will bring it back for review.</p>
            </div>
          ) : null}

          <div role="log" aria-label="Conversation" aria-relevant="additions" className="space-y-4">
            {/* displays older messages depending on their role and kind */}
            {chat.messages.map((item) => (
              <article key={item.id} className={`max-w-[95%] rounded-2xl border px-4 py-3 sm:max-w-[90%] ${item.role === "user" ? "ml-auto border-border bg-primary-subtle" : item.kind === "cancelled" ? "border-coral/40 bg-cream" : item.kind === "completed" ? "border-success/30 bg-success-subtle" : "border-sky/30 bg-surface-card"}`}>
                <p className="mb-1 text-xs font-extrabold text-text-muted">{item.role === "user" ? "You" : "StudyOps Assistant"}{item.kind !== "chat" ? ` · ${item.kind === "command" ? "Command" : item.kind === "cancelled" ? "Cancelled" : "Completed"}` : ""}</p>
                <p className="whitespace-pre-wrap wrap-anywhere text-sm leading-7 text-text-strong">{item.text}</p>
              </article>
            ))}
          </div>
            {/* displays the status of the conversation */}
          <p role="status" className="text-sm font-semibold text-primary-dark">{busy ? chat.pending === "approve" ? "Accepting your schedule…" : chat.pending === "cancel" ? "Cancelling the draft…" : chat.pending === "edit" ? "Revising your draft…" : "The assistant is working on your message…" : ""}</p>

          {reviewing ? (
            // if currently reviewing a draft, display the schedule review section with options to accept, cancel, or request changes
            // displays the schedule review section with options to accept, cancel, or request changes
            <section ref={reviewRef} tabIndex={-1} aria-labelledby="review-title" aria-busy={busy} className="rounded-2xl border-2 border-accent bg-cream p-4 outline-none focus-visible:ring-3 focus-visible:ring-primary sm:p-5">
              <p className="text-xs font-extrabold uppercase tracking-brand text-accent-deep">Command · Awaiting your review</p>
              <h2 id="review-title" className="mt-2 text-xl font-extrabold text-text-strong">Accept, cancel, or request changes</h2>
                {/* displays the schedule review */}
              <div className="mt-4"><AssistantScheduleReview reviews={chat.reviews} subjects={subjects} timezone={timezone} /></div>
            {/* displays the command options */}
              <div className="mt-5 flex flex-wrap gap-3">
                <button type="button" disabled={locked || confirmCancel} onClick={() => { void chat.command({ action: "approve" }); }} className={`${button} bg-accent text-text-strong shadow-accent-glow hover:bg-accent-light`}>{chat.pending === "approve" ? "Accepting…" : "Accept"}</button>
                <button ref={cancelRef} type="button" aria-expanded={confirmCancel} aria-controls="cancel-draft-confirmation" disabled={locked} onClick={() => setConfirmCancel(true)} className={`${button} border border-error-dark bg-surface-card text-error-dark hover:bg-coral/10`}>Cancel</button>
              </div>

              {confirmCancel ? (
                <div ref={confirmRef} id="cancel-draft-confirmation" tabIndex={-1} role="group" aria-label="Discard this draft schedule?" onKeyDown={(event) => { if (event.key === "Escape" && !locked) handleKeepDraft(); }} className="mt-4 rounded-xl border border-coral/40 bg-surface-card p-4 outline-none focus:ring-3 focus:ring-coral/40">
                  <p className="text-sm font-bold text-error-dark">Discard this draft schedule?</p>
                  <p className="mt-1 text-sm text-text">Its proposed tasks and sessions will not be created.</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button type="button" disabled={locked} onClick={async () => { if (await chat.command({ action: "cancel" })) setConfirmCancel(false); }} className={`${button} bg-error-dark text-white hover:bg-text-strong`}>Yes, cancel draft</button>
                    <button type="button" disabled={locked} onClick={handleKeepDraft} className={`${button} border border-border text-text-strong hover:bg-cream`}>Keep draft</button>
                  </div>
                </div>
              ) : null}
              {/* displays the feedback form for editing the draft */}
              <form onSubmit={handleEdit} className="mt-5 border-t border-dashed border-accent-dark/50 pt-4">
                <label htmlFor="assistant-feedback" className="text-sm font-bold text-text-strong">What would you like to change?</label>
                <textarea id="assistant-feedback" name="feedback" required maxLength={8000} rows={3} value={feedback} disabled={locked || confirmCancel} onChange={(event) => setFeedback(event.target.value)} placeholder="Move Monday's session to Tuesday…" className={input} />
                <button type="submit" disabled={locked || confirmCancel || !feedback.trim()} className={`${button} mt-3 bg-primary-dark text-white hover:bg-text-strong`}>{chat.pending === "edit" ? "Submitting changes…" : "Submit changes"}</button>
              </form>
            </section>
          ) : null}
            {/* displays the error message */}
          {chat.error ? (
            <div ref={errorRef} tabIndex={-1} role="alert" className="rounded-xl border border-coral/40 bg-surface-card p-4 text-sm leading-6 text-error-dark outline-none focus:ring-3 focus:ring-coral/40">
              <p>{chat.error}</p>
              <div className="mt-2 flex flex-wrap gap-4 font-bold">
                <Link to="/app/tasks" className="underline focus-visible:outline-3 focus-visible:outline-primary">View tasks</Link>
                <Link to="/app/study-sessions" className="underline focus-visible:outline-3 focus-visible:outline-primary">View sessions</Link>
                {chat.error.includes("Log in") ? <Link to="/login" className="underline focus-visible:outline-3 focus-visible:outline-primary">Log in</Link> : null}
              </div>
            </div>
          ) : null}
          <div ref={endRef} />
        </div>
      </div>
      {/* displays the message input area */}
      <div className="border-t border-border bg-surface-card p-4 sm:p-6">
        <form onSubmit={handleSend} aria-busy={busy} className="mx-auto max-w-3xl">
          <label htmlFor="assistant-message" className="text-sm font-bold text-text-strong">Message the StudyOps Assistant</label>
          <textarea ref={messageRef} id="assistant-message" name="user_input" required rows={3} maxLength={8000} value={message} onChange={(event) => setMessage(event.target.value)} disabled={locked || reviewing} aria-describedby="message-help" placeholder="Help me plan my study time…" className={`${input} bg-cream`} />
          <div className="mt-3 flex items-center justify-between gap-4">
            <p id="message-help" className="text-xs leading-5 text-text-muted">{reviewing ? "Review the draft above to continue." : "Chat with your assistant. Proposed schedules appear separately for review."}</p>
            <button type="submit" disabled={locked || reviewing || !message.trim()} className={`${button} shrink-0 bg-accent text-text-strong hover:bg-accent-light`}>{chat.pending === "send" ? "Sending…" : "Send"}</button>
          </div>
        </form>
      </div>
    </>
  );
}
