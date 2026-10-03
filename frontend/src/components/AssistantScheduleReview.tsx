import type { ScheduleReview } from "../types/assistant";
import type { Subject } from "../types/subjects";

type AssistantScheduleReviewProps = {
  reviews: ScheduleReview[];
  subjects: Subject[];
  timezone: string;
};

export function AssistantScheduleReview({ reviews, subjects, timezone }: AssistantScheduleReviewProps) {
  const date = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short", timeZone: timezone });
  return (
    <div className="space-y-5">
      {reviews.map((review, index) => (
        <div key={`${review.type}-${index}`}>
          <h3 className="text-lg font-extrabold text-text-strong">{review.title}</h3>
          <p className="mt-1 text-sm text-text-muted">Times in {timezone}. These tasks and sessions are a draft until you accept.</p>
          <div className="mt-4 space-y-3">
            {review.draft.drafts.map(({ task, study_sessions }) => (
              <article key={task.draft_task_id} className="min-w-0 rounded-2xl border border-border border-l-4 border-l-primary bg-surface-card p-4">
                <p className="text-xs font-bold uppercase tracking-wide text-primary-dark">{subjects.find((subject) => subject.id === task.subject)?.name ?? `Subject ${task.subject}`}</p>
                <h4 className="mt-1 wrap-anywhere font-extrabold text-text-strong">{task.title}</h4>
                <p className="mt-2 whitespace-pre-wrap wrap-anywhere text-sm leading-6">{task.description}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-text">
                  <span className="rounded-lg bg-primary-subtle px-2 py-1 capitalize">{task.task_type}</span>
                  <span className="rounded-lg bg-cream px-2 py-1 capitalize">{task.task_priority} priority</span>
                  <span className="rounded-lg bg-sky-subtle px-2 py-1">{task.estimated_minutes} minutes</span>
                </div>
                <p className="mt-3 text-sm font-semibold">Due <time dateTime={task.due_date}>{date.format(new Date(task.due_date))}</time></p>
                <ul aria-label={`Study sessions for ${task.title}`} className="mt-3 space-y-2 border-t border-dashed border-border pt-3 text-sm">
                  {study_sessions.map((session) => (
                    <li key={session.draft_session_id} className="rounded-xl bg-primary-subtle px-3 py-2 leading-6">
                      <time dateTime={session.start_at}>{date.format(new Date(session.start_at))}</time>
                      <span aria-hidden="true"> → </span><span className="sr-only"> until </span>
                      <time dateTime={session.end_at}>{date.format(new Date(session.end_at))}</time>
                    </li>
                  ))}
                </ul>
              </article>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
