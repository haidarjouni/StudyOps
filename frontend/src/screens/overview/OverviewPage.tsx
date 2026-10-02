import { useEffect } from "react";
import { Link, useLoaderData, useSearchParams } from "react-router";
import {
    card,
    EmptyState,
    PageHeading,
    secondary,
} from "../../components/DashboardParts";
import type { overviewLoader } from "./loaders";

function when(value: string) {
    return new Intl.DateTimeFormat(undefined, {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value));
}

export function OverviewPage() {
    const [searchParams] = useSearchParams();
    const {
        subjects,
        tasks,
        sessions,
        now: currentTime,
    } = useLoaderData<typeof overviewLoader>();
    useEffect(() => {
        document.title = "Overview | StudyOps";
    }, []);
    const now = new Date(currentTime).getTime();
    // Filter out tasks that are done or cancelled, and sort by due date
    const upcoming = tasks
        .filter(
            (task) =>
                task.task_status !== "done" &&
                task.task_status !== "cancelled" &&
                new Date(task.due_date).getTime() >= now,
        )
        .sort((a, b) => a.due_date.localeCompare(b.due_date));
    // Filter out sessions that are not scheduled, and sort by start time
    const scheduled = sessions
        .filter((session) => session.status === "scheduled")
        .sort((a, b) => a.start_at.localeCompare(b.start_at));

    const weekEnd = now + 7 * 24 * 60 * 60 * 1000;
    // calculate the total number of minutes of scheduled sessions in the next 7 days
    const minutes = scheduled
        .filter((session) => new Date(session.start_at).getTime() < weekEnd)
        .reduce(
            (sum, session) =>
                sum +
                Math.max(
                    0,
                    (new Date(session.end_at).getTime() -
                        new Date(session.start_at).getTime()) /
                        60000,
                ),
            0,
        );

    return (
        <>
            <PageHeading
                title="Your study overview"
                description="A clear view of what needs your attention."
                addTo="/app/tasks/new"
                addLabel="Add task"
            />
            {searchParams.get("chat_deleted") === "1" ? (
                <p role="status" className="mb-6 rounded-xl border border-success/25 bg-success-subtle px-4 py-3 font-semibold text-text-strong">
                    Chat deleted.
                </p>
            ) : null}
            {/* mapping to show the cards  */}
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {[
                    ["Subjects", subjects.length],
                    ["Upcoming tasks", upcoming.length],
                    ["Scheduled sessions", scheduled.length],
                    ["Study minutes in next 7 days", Math.round(minutes)],
                ].map(([label, count]) => (
                    <div
                        key={label}
                        className={`${card} border-l-4 border-l-primary`}
                    >
                        <p className="text-sm font-bold text-text-muted">
                            {label}
                        </p>
                        <p className="mt-3 text-3xl font-extrabold text-text-strong">
                            {count}
                        </p>
                    </div>
                ))}
            </div>

            <div className="mt-8 grid gap-6 xl:grid-cols-2">
                <section>
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <h2 className="text-2xl font-extrabold">
                            Next deadlines
                        </h2>
                        <Link
                            to="/app/tasks"
                            className="font-bold text-primary-dark underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-primary"
                        >
                            All tasks
                        </Link>
                    </div>
                    {/* if there are upcoming tasks, display them; otherwise, show an empty state */}
                    {upcoming.length ? (
                        <ul className="space-y-3">
                            {/* get most recent 5 tasks */}
                            {upcoming.slice(0, 4).map((task) => (
                                <li key={task.id} className={card}>
                                    <Link
                                        to={`/app/tasks/${task.id}`}
                                        className="font-extrabold text-primary-dark underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-primary"
                                    >
                                        {task.title}
                                    </Link>
                                    {/* search for the related subject and display its code */}
                                    <p className="mt-1 text-sm text-text-muted">
                                        {subjects.find(
                                            (subject) =>
                                                subject.id === task.subject,
                                        )?.code ?? "Subject"}{" "}
                                        · Due {when(task.due_date)}
                                    </p>

                                    <p className="mt-2 text-sm font-semibold capitalize">
                                        {task.task_priority} priority ·{" "}
                                        {task.task_status.replace("_", " ")}
                                    </p>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <EmptyState
                            title="No upcoming deadlines"
                            description="Add a task to keep your next deadline in view."
                            to="/app/tasks/new"
                            action="Add task"
                        />
                    )}
                </section>

                <section>
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <h2 className="text-2xl font-extrabold">
                            Next sessions
                        </h2>
                        <Link
                            to="/app/study-sessions"
                            className="font-bold text-primary-dark underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-primary"
                        >
                            All sessions
                        </Link>
                    </div>
                    {/* show the next 4 scheduled sessions */}
                    {scheduled.length ? (
                        <ul className="space-y-3">
                            {scheduled.slice(0, 4).map((session) => (
                                <li key={session.id} className={card}>
                                    <Link
                                        to={`/app/study-sessions/${session.id}`}
                                        className="font-extrabold text-primary-dark underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-primary"
                                    >
                                        {session.subject.name}
                                    </Link>
                                    <p className="mt-1 text-sm text-text-muted">
                                        {when(session.start_at)} ·{" "}
                                        {session.task?.title ?? "General study"}
                                    </p>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <EmptyState
                            title="No sessions scheduled"
                            description="Set aside time for focused study."
                            to="/app/study-sessions/new"
                            action="Schedule a session"
                        />
                    )}
                </section>
            </div>
            
            <div className="mt-8 flex flex-wrap gap-3">
                <Link className={secondary} to="/app/subjects/new">
                    Add subject
                </Link>
                <Link className={secondary} to="/app/study-sessions/new">
                    Schedule session
                </Link>
            </div>
        </>
    );
}
