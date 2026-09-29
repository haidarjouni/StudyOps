import { useEffect } from "react";
import {
  Form,
  Link,
  useLoaderData,
  useNavigation,
  useSearchParams,
} from "react-router";
import {
  card,
  danger,
  PageHeading,
  secondary,
} from "../../components/DashboardParts";
import type { sessionLoader } from "./loaders";
export function SessionDetailPage() {
    // get the session
  const { session } = useLoaderData<typeof sessionLoader>();
//   get query string
  const [params] = useSearchParams();
  const navigation = useNavigation();
  useEffect(() => {
    document.title = `${session.subject.name} session | StudyOps`;
  }, [session.subject.name]);
  function handleDelete(event: React.FormEvent<HTMLFormElement>) {
    if (!window.confirm("Delete this study session?")) event.preventDefault();
  }
  const date = (iso: string) =>
    new Intl.DateTimeFormat(undefined, {
      dateStyle: "full",
      timeStyle: "short",
    }).format(new Date(iso));
  return (
    <>
      <PageHeading
        title={session.subject.name}
        description={`${session.subject.code} · ${session.status}`}
      />
      {/* if the session was saved successfully */}
      {params.get("saved") === "1" && (
        <p
          role="status"
          className="mb-5 rounded-xl bg-success-subtle p-4 font-semibold text-success"
        >
          Session saved.
        </p>
      )}
      <div className={`${card} max-w-3xl`}>
        <dl className="grid gap-5 sm:grid-cols-2">
          <div>
            <dt className="text-sm text-text-muted">Starts</dt>
            <dd className="font-bold">{date(session.start_at)}</dd>
          </div>
          <div>
            <dt className="text-sm text-text-muted">Ends</dt>
            <dd className="font-bold">{date(session.end_at)}</dd>
          </div>
          <div>
            <dt className="text-sm text-text-muted">Task</dt>
            <dd className="font-bold">
              {session.task?.title ?? "General study"}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-text-muted">Status</dt>
            <dd className="font-bold capitalize">{session.status}</dd>
          </div>
        </dl>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            to={`/app/study-sessions/${session.id}/edit`}
            className={secondary}
          >
            Edit session
          </Link>
          <Form
            method="post"
            action={`/app/study-sessions/${session.id}/delete`}
            onSubmit={handleDelete}
          >
            <button
              disabled={navigation.state === "submitting"}
              className={danger}
            >
              Delete session
            </button>
          </Form>
        </div>
      </div>
    </>
  );
}
