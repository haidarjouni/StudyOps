import type { ReactNode } from 'react'
import { Link } from 'react-router'
import { HowItWorksSection } from '../../components/HowItWorksSection'

function BrandMark() {
  return (
    <span
      className="relative flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary shadow-primary-glow"
      aria-hidden="true"
    >
      <svg viewBox="0 0 32 32" className="size-7 fill-none">
        <path
          d="M7 8.5c3.6 0 6.4 1.1 9 3.2v13.1c-2.6-2.1-5.4-3.2-9-3.2V8.5Z"
          className="fill-surface-card"
        />
        <path
          d="M25 8.5c-3.6 0-6.4 1.1-9 3.2v13.1c2.6-2.1 5.4-3.2 9-3.2V8.5Z"
          className="fill-cream"
        />
        <path
          d="M16 11.7v13.1"
          className="stroke-primary-dark"
          strokeWidth="1.8"
          strokeLinecap="round"
        />
        <path
          d="m21.1 5.6 1 2 2.2.3-1.6 1.5.4 2.2-2-1-2 1 .4-2.2L18 7.9l2.1-.3 1-2Z"
          className="fill-accent"
        />
      </svg>
    </span>
  )
}

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      className="size-5 shrink-0"
      aria-hidden="true"
    >
      <circle cx="10" cy="10" r="9" className="fill-primary-subtle" />
      <path
        d="m6.2 10.1 2.4 2.4 5.2-5.2"
        className="fill-none stroke-primary-dark"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

function PlannerPreview() {
  return (
    <div
      className="relative mx-auto w-full min-w-0 max-w-xl pt-6 lg:pt-0"
      aria-hidden="true"
    >
      <div className="absolute -left-3 top-3 h-24 w-24 rounded-full bg-accent-light/60 blur-2xl sm:left-5 lg:-top-5" />
      <div className="absolute -right-1 bottom-12 h-28 w-28 rounded-full bg-coral-light/30 blur-3xl" />

      <div className="relative rotate-1 rounded-3xl border border-primary/20 bg-surface-card p-4 shadow-card sm:p-6">
        <div className="flex items-center justify-between border-b border-dashed border-border pb-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-brand text-primary-dark">
              Today’s study plan
            </p>
            <p className="mt-1 text-lg font-extrabold text-text-strong">
              A calm, focused afternoon
            </p>
          </div>
          <div className="flex size-12 items-center justify-center rounded-2xl bg-accent text-sm font-extrabold text-text-strong shadow-accent-glow">
            3/4
          </div>
        </div>

        <div className="mt-5 grid grid-cols-[3.5rem_1fr] gap-x-3 gap-y-3 sm:grid-cols-[4.5rem_1fr] sm:gap-x-4">
          <p className="pt-3 text-right text-xs font-bold text-text-muted">3:00</p>
          <div className="rounded-2xl border border-primary/20 border-l-4 border-l-primary bg-primary-subtle p-3 shadow-subtle sm:p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wide text-primary-dark">
                  Mathematics
                </p>
                <p className="mt-1 text-sm font-extrabold text-text-strong sm:text-base">
                  Practice problem set
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-surface-card px-2.5 py-1 text-xs font-bold text-primary-dark">
                45 min
              </span>
            </div>
          </div>

          <p className="pt-3 text-right text-xs font-bold text-text-muted">4:00</p>
          <div className="rounded-2xl border border-sky/20 border-l-4 border-l-sky bg-sky-subtle p-3 sm:p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wide text-sky-dark">
                  Biology
                </p>
                <p className="mt-1 text-sm font-extrabold text-text-strong sm:text-base">
                  Review cell structure
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-surface-card px-2.5 py-1 text-xs font-bold text-sky-dark">
                30 min
              </span>
            </div>
          </div>

          <p className="pt-2 text-right text-xs font-bold text-text-muted">4:30</p>
          <div className="flex items-center gap-2 px-1 py-2 text-xs font-bold uppercase tracking-wide text-text-muted">
            <span className="h-px flex-1 border-t border-dashed border-border" />
            10 min reset
            <span className="h-px flex-1 border-t border-dashed border-border" />
          </div>

          <p className="pt-3 text-right text-xs font-bold text-text-muted">4:40</p>
          <div className="rounded-2xl border border-accent-dark/20 border-l-4 border-l-accent-dark bg-cream p-3 sm:p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="text-xs font-bold uppercase tracking-wide text-accent-deep">
                  Literature
                </p>
                <p className="mt-1 text-sm font-extrabold text-text-strong sm:text-base">
                  Outline essay response
                </p>
              </div>
              <span className="shrink-0 rounded-full bg-surface-card px-2.5 py-1 text-xs font-bold text-accent-deep">
                50 min
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute -bottom-5 -left-2 -rotate-3 rounded-2xl border border-success/20 bg-surface-card px-4 py-3 shadow-card sm:left-4">
        <div className="flex items-center gap-3">
          <span className="flex size-9 items-center justify-center rounded-full bg-success-subtle text-success">
            <svg viewBox="0 0 20 20" className="size-5 fill-none">
              <path
                d="m5.2 10.2 3 3 6.6-6.6"
                className="stroke-current"
                strokeWidth="2.2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </span>
          <div>
            <p className="text-xs font-bold text-text-muted">You’re on track</p>
            <p className="text-sm font-extrabold text-text-strong">One step at a time</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function FeatureIcon({ children, className }: FeatureIconProps) {
  return (
    <span
      className={`flex size-11 shrink-0 items-center justify-center rounded-xl ${className}`}
    >
      {children}
    </span>
  )
}

interface FeatureIconProps {
  children: ReactNode
  className: string
}

export function WelcomePage() {
  return (
    <div className="relative isolate min-h-svh overflow-x-clip bg-surface-base text-text">
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-96 bg-hero-glow" />
      <div className="pointer-events-none absolute left-[8%] top-40 -z-10 size-3 rotate-12 rounded-sm bg-coral sm:size-4" />
      <div className="pointer-events-none absolute right-[9%] top-28 -z-10 size-4 rounded-full border-[3px] border-primary sm:size-5" />

      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
        <div className="flex items-center gap-3">
          <BrandMark />
          <span className="text-xl font-extrabold tracking-tight text-text-strong sm:text-2xl">
            Study<span className="text-primary-dark">Ops</span>
          </span>
        </div>

        <div className="hidden items-center gap-3 sm:flex">
          <Link
            to="/login"
            className="min-h-11 rounded-full flex items-center px-5 text-sm font-extrabold text-primary-dark transition-colors duration-200 hover:bg-primary-subtle focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:bg-primary-subtle motion-reduce:transition-none"
          >
            Log in
          </Link>
          <Link
            to="/register"
            className="inline-flex min-h-11 items-center rounded-full bg-accent px-6 text-sm font-extrabold text-text-strong shadow-accent-glow transition duration-200 hover:-translate-y-0.5 hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:translate-y-0 active:bg-accent-dark motion-reduce:transform-none motion-reduce:transition-none"
          >
            Create account
          </Link>
        </div>
      </header>

      <main>
        <section className="mx-auto grid w-full max-w-7xl grid-cols-[minmax(0,1fr)] items-center gap-14 px-4 pb-20 pt-10 sm:px-6 sm:pb-24 sm:pt-16 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)] lg:gap-20 lg:px-8 lg:pb-28 lg:pt-20">
          <div className="min-w-0 max-w-2xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-surface-card px-3.5 py-2 text-xs font-extrabold uppercase tracking-brand text-primary-dark shadow-subtle">
              <span className="size-2 rounded-full bg-coral" />
              Your study life, organized
            </div>

            <h1 className="mt-7 text-5xl font-extrabold leading-[1.02] tracking-tight text-text-strong sm:text-6xl lg:text-7xl">
              Make space for
              <span className="relative mt-2 block w-fit text-primary-dark">
                focused study.
                <svg
                  viewBox="0 0 420 18"
                  preserveAspectRatio="none"
                  className="absolute -bottom-2 left-0 -z-10 h-3 w-full text-accent sm:h-4"
                  aria-hidden="true"
                >
                  <path
                    d="M4 11C104 2 245 4 416 9"
                    className="fill-none stroke-current"
                    strokeWidth="10"
                    strokeLinecap="round"
                  />
                </svg>
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-lg leading-8 text-text-muted sm:text-xl sm:leading-9">
              Bring subjects, deadlines, and study sessions together in one calm
              workspace—so you always know what to focus on next.
            </p>

            <div className="mt-9 flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link
                to="/register"
                className="inline-flex min-h-13 items-center justify-center rounded-xl bg-accent px-7 py-3.5 text-base font-extrabold text-text-strong shadow-accent-glow transition duration-200 hover:-translate-y-0.5 hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:translate-y-0 active:bg-accent-dark motion-reduce:transform-none motion-reduce:transition-none"
              >
                Create your account
              </Link>
              <Link
                to="/login"
                className="min-h-13 rounded-xl border-2 border-primary bg-surface-card px-7 py-3 text-base font-extrabold text-primary-dark shadow-subtle transition duration-200 hover:-translate-y-0.5 hover:bg-primary-subtle focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:translate-y-0 motion-reduce:transform-none motion-reduce:transition-none"
              >
                Log in
              </Link>
            </div>

            <ul className="mt-8 grid gap-3 text-sm font-bold text-text sm:grid-cols-3 sm:gap-4">
              <li className="flex items-center gap-2">
                <CheckIcon />
                Plan clearly
              </li>
              <li className="flex items-center gap-2">
                <CheckIcon />
                Stay on track
              </li>
              <li className="flex items-center gap-2">
                <CheckIcon />
                Study your way
              </li>
            </ul>
          </div>

          <PlannerPreview />
        </section>

        <HowItWorksSection />

        <section className="border-t border-primary/15 bg-surface-card/70">
          <div className="mx-auto grid w-full max-w-7xl gap-7 px-4 py-8 sm:grid-cols-3 sm:px-6 sm:py-10 lg:px-8">
            <div className="flex gap-4">
              <FeatureIcon className="bg-primary-subtle text-primary-dark">
                <svg viewBox="0 0 24 24" className="size-6 fill-none" aria-hidden="true">
                  <path d="M7 3v3M17 3v3M4 9h16M6 5h12a2 2 0 0 1 2 2v12H4V7a2 2 0 0 1 2-2Z" className="stroke-current" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="m8 14 2 2 5-5" className="stroke-current" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </FeatureIcon>
              <div>
                <h2 className="font-extrabold text-text-strong">Plan with confidence</h2>
                <p className="mt-1 text-sm leading-6 text-text-muted">Turn deadlines into a schedule you can actually follow.</p>
              </div>
            </div>

            <div className="flex gap-4">
              <FeatureIcon className="bg-cream text-accent-deep">
                <svg viewBox="0 0 24 24" className="size-6 fill-none" aria-hidden="true">
                  <path d="M6 5.5h9.5A2.5 2.5 0 0 1 18 8v11H8.5A2.5 2.5 0 0 1 6 16.5v-11Z" className="stroke-current" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  <path d="M6 16.5A2.5 2.5 0 0 1 8.5 14H18M10 9h4" className="stroke-current" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </FeatureIcon>
              <div>
                <h2 className="font-extrabold text-text-strong">Keep it all together</h2>
                <p className="mt-1 text-sm leading-6 text-text-muted">Organize every subject, task, and session in one place.</p>
              </div>
            </div>

            <div className="flex gap-4">
              <FeatureIcon className="bg-sky-subtle text-sky-dark">
                <svg viewBox="0 0 24 24" className="size-6 fill-none" aria-hidden="true">
                  <path d="M12 3 9.7 8.2 4 9l4.2 4-1.1 5.7L12 16l4.9 2.7-1.1-5.7L20 9l-5.7-.8L12 3Z" className="stroke-current" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </FeatureIcon>
              <div>
                <h2 className="font-extrabold text-text-strong">Build steady momentum</h2>
                <p className="mt-1 text-sm leading-6 text-text-muted">Make progress visible without adding pressure.</p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}
