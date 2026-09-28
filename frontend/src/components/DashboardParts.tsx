import {
    Link,
    useRouteError,
    isRouteErrorResponse,
    useRevalidator,
} from "react-router";

export const primary =
    "inline-flex min-h-11 items-center justify-center rounded-xl bg-accent px-5 py-2.5 text-sm font-extrabold text-text-strong shadow-accent-glow transition-colors hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-60 motion-reduce:transition-none";

export const secondary =
    "inline-flex min-h-11 items-center justify-center rounded-xl border border-primary-dark px-5 py-2.5 text-sm font-bold text-primary-dark transition-colors hover:bg-primary-subtle focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-60 motion-reduce:transition-none";

export const danger =
    "inline-flex min-h-11 items-center justify-center rounded-xl border border-coral-dark px-5 py-2.5 text-sm font-bold text-coral-dark transition-colors hover:bg-coral/10 focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-coral disabled:opacity-60 motion-reduce:transition-none";

export const input =
    "min-h-11 w-full rounded-xl border border-border bg-cream px-4 py-2.5 text-text-strong outline-none focus-visible:border-primary-dark focus-visible:ring-3 focus-visible:ring-primary/25 aria-invalid:border-coral-dark";

export const card =
    "min-w-0 break-words rounded-2xl border border-border bg-surface-card p-5 shadow-card sm:p-6";

export function PageHeading({
    title,
    description,
    addTo,
    addLabel,
}: {
    title: string;
    description: string;
    addTo?: string;
    addLabel?: string;
}) {
    return (
        <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0 break-words">
                <h1 className="text-3xl font-extrabold tracking-tight text-text-strong sm:text-4xl">
                    {title}
                </h1>
                <p className="mt-2 text-text-muted">{description}</p>
            </div>
            {/* link takes u to the desired page with a color scheme */}
            {addTo && addLabel ? (
                <Link to={addTo} className={primary}>
                    + {addLabel}
                </Link>
            ) : null}
        </div>
    );
}

export function EmptyState({
    title,
    description,
    to,
    action,
}: {
    title: string;
    description: string;
    to?: string;
    action?: string;
}) {
    return (
        <div className={`${card} py-12 text-center`}>
            <div
                className="mx-auto flex size-14 items-center justify-center rounded-2xl bg-primary-subtle text-2xl font-black text-primary-dark"
                aria-hidden="true"
            >
                ◇
            </div>
            <h2 className="mt-5 text-xl font-extrabold">{title}</h2>
            <p className="mx-auto mt-2 max-w-md text-text-muted">
                {description}
            </p>
            {to && action ? (
                <Link className={`${primary} mt-6`} to={to}>
                    {action}
                </Link>
            ) : null}
        </div>
    );
}

export function RouteErrorPage() {
    const error = useRouteError();
    const revalidator = useRevalidator();
    const status = isRouteErrorResponse(error)
        ? error.status
        : typeof error === "object" && error && "status" in error
          ? Number(error.status)
          : 0;
    const title =
        status === 404
            ? "This record is unavailable"
            : status === 401
              ? "Your session has expired"
              : "We couldn’t load this page";
    return (
        <div className="mx-auto max-w-2xl px-4 py-20">
            <div className={card}>
                <h1 className="text-3xl font-extrabold">{title}</h1>
                <p className="mt-3 text-text-muted">
                    {status === 404
                        ? "It may have been removed or you may not have access."
                        : status === 401
                          ? "Log in to continue."
                          : "Check your connection and try again."}
                </p>
                <div className="mt-6 flex flex-wrap gap-3">
                    <button
                        type="button"
                        className={primary}
                        onClick={() => revalidator.revalidate()}
                    >
                        Try again
                    </button>
                    <Link
                        to={status === 401 ? "/login" : "/app"}
                        className={secondary}
                    >
                        {status === 401 ? "Log in" : "Go to overview"}
                    </Link>
                </div>
            </div>
        </div>
    );
}