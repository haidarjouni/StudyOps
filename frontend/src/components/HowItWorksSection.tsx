function AddWhatMattersIcon() {
  return (
    <svg viewBox="0 0 28 28" className="size-7 fill-none" aria-hidden="true">
      <path
        d="M8.5 5.5h11A2.5 2.5 0 0 1 22 8v14.5H6V8a2.5 2.5 0 0 1 2.5-2.5Z"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M10.5 4h7v3.5h-7V4ZM10 12h8M10 16h5"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M18.5 19.5v5M16 22h5"
        className="stroke-coral-dark"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}

function BuildPlanIcon() {
  return (
    <svg viewBox="0 0 28 28" className="size-7 fill-none" aria-hidden="true">
      <path
        d="M6 7.5h16A2.5 2.5 0 0 1 24.5 10v12.5h-21V10A2.5 2.5 0 0 1 6 7.5Z"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M9 4.5v5M19 4.5v5M4 12h20"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M8 16h4v3H8zM16 16h4v3h-4z"
        className="fill-current"
      />
    </svg>
  )
}

function ReviewPlanIcon() {
  return (
    <svg viewBox="0 0 28 28" className="size-7 fill-none" aria-hidden="true">
      <path
        d="M8 4.5h9l5 5v14H8v-19Z"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M17 4.5v5h5M11.5 15.5l2 2 4.5-4.5"
        className="stroke-current"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function HowItWorksSection() {
  return (
    <section
      className="relative border-y border-primary/15 bg-surface-card px-4 py-20 sm:px-6 sm:py-24 lg:px-8 lg:py-28"
      aria-labelledby="how-studyops-works-title"
    >
      <div className="pointer-events-none absolute left-[7%] top-20 size-3 rotate-12 rounded-sm bg-coral sm:size-4" />
      <div className="pointer-events-none absolute bottom-20 right-[8%] size-4 rounded-full bg-accent sm:size-5" />

      <div className="mx-auto w-full max-w-7xl">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">
            How StudyOps works
          </p>
          <h2
            id="how-studyops-works-title"
            className="mt-3 text-3xl font-extrabold tracking-tight text-text-strong sm:text-4xl"
          >
            From busy week to clear plan.
          </h2>
          <p className="mx-auto mt-5 max-w-xl text-base leading-7 text-text-muted sm:text-lg sm:leading-8">
            StudyOps helps you turn everything you need to do into a schedule that
            feels manageable.
          </p>
        </div>

        <div className="relative mx-auto mt-12 max-w-6xl sm:mt-16">
          <div
            className="pointer-events-none absolute bottom-10 left-8 top-10 border-l-2 border-dashed border-primary/30 md:bottom-auto md:left-[16.666%] md:right-[16.666%] md:top-11 md:border-l-0 md:border-t-2"
            aria-hidden="true"
          />

          <ol className="relative grid gap-6 md:grid-cols-3 md:gap-5 lg:gap-8">
            <li className="relative z-10 rounded-3xl border border-accent-dark/20 bg-cream p-6 shadow-card sm:p-7">
              <span
                className="absolute right-5 top-5 size-3 rotate-12 rounded-sm bg-coral"
                aria-hidden="true"
              />
              <div className="flex items-center gap-4 md:block">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl border border-primary/20 bg-surface-card text-primary-dark shadow-subtle md:mb-6">
                  <AddWhatMattersIcon />
                </div>
                <div>
                  <p className="text-xs font-extrabold uppercase tracking-brand text-coral-dark">
                    Step 01
                  </p>
                  <h3 className="mt-1 text-xl font-extrabold text-text-strong md:mt-2">
                    Add what matters
                  </h3>
                </div>
              </div>
              <p className="mt-5 leading-7 text-text-muted">
                Organize your subjects, tasks, exams, and deadlines.
              </p>
            </li>

            <li className="relative z-10 rounded-3xl border border-sky/30 bg-sky-subtle p-6 shadow-card sm:p-7 md:-translate-y-3">
              <span
                className="absolute right-5 top-5 size-4 rounded-full bg-accent"
                aria-hidden="true"
              />
              <div className="flex items-center gap-4 md:block">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl border border-sky/30 bg-surface-card text-sky-dark shadow-subtle md:mb-6">
                  <BuildPlanIcon />
                </div>
                <div>
                  <p className="text-xs font-extrabold uppercase tracking-brand text-sky-dark">
                    Step 02
                  </p>
                  <h3 className="mt-1 text-xl font-extrabold text-text-strong md:mt-2">
                    Build your study plan
                  </h3>
                </div>
              </div>
              <p className="mt-5 leading-7 text-text-muted">
                Turn your workload into focused sessions with realistic breaks.
              </p>
            </li>

            <li className="relative z-10 rounded-3xl border border-primary/20 bg-surface-card p-6 shadow-card sm:p-7">
              <span
                className="absolute right-5 top-5 h-3 w-6 -rotate-6 rounded-full bg-coral-light"
                aria-hidden="true"
              />
              <div className="flex items-center gap-4 md:block">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl border border-primary/20 bg-primary-subtle text-primary-dark shadow-subtle md:mb-6">
                  <ReviewPlanIcon />
                </div>
                <div>
                  <p className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">
                    Step 03
                  </p>
                  <h3 className="mt-1 text-xl font-extrabold text-text-strong md:mt-2">
                    Review and make it yours
                  </h3>
                </div>
              </div>
              <p className="mt-5 leading-7 text-text-muted">
                Adjust and approve the plan before adding it to your schedule.
              </p>
            </li>
          </ol>
        </div>
      </div>
    </section>
  )
}
