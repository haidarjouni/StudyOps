import { useEffect, useRef } from 'react'
import { Link, useFetcher, useSearchParams } from 'react-router'
import { RegistrationField } from '../../components/RegistrationField'
import type { loginAction } from './actions'

export function LoginPage() {
  const fetcher = useFetcher<typeof loginAction>()
  const [searchParams] = useSearchParams()
  const formRef = useRef<HTMLFormElement>(null)
  const successRef = useRef<HTMLDivElement>(null)
  const isSubmitting = fetcher.state !== 'idle'
  const result = isSubmitting ? undefined : fetcher.data
  const errors = result?.ok === false ? result.errors : undefined
  const isSignedIn = Boolean(result && 'ok' in result && result.ok)

  useEffect(() => {
    document.title = 'Log in | StudyOps'
  }, [])

  useEffect(() => {
    if (!errors) return
    const invalidField = formRef.current?.querySelector<HTMLInputElement>('[aria-invalid="true"]')
    const summary = formRef.current?.querySelector<HTMLDivElement>('[data-error-summary]')
    ;(invalidField || summary)?.focus()
  }, [errors])

  useEffect(() => {
    if (isSignedIn) successRef.current?.focus()
  }, [isSignedIn])

  return (
    <div className="relative isolate min-h-svh overflow-x-clip bg-surface-base text-text">
      <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-96 bg-hero-glow" />
      <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-5 sm:px-6 sm:py-6 lg:px-8">
        <Link to="/" className="flex min-h-11 items-center gap-3 rounded-xl focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary">
          <span className="flex size-11 items-center justify-center rounded-2xl bg-primary text-2xl font-extrabold text-surface-card shadow-primary-glow" aria-hidden="true">S</span>
          <span className="text-xl font-extrabold tracking-tight text-text-strong sm:text-2xl">Study<span className="text-primary-dark">Ops</span></span>
        </Link>
        <Link to="/" className="rounded-full px-4 py-3 text-sm font-bold text-primary-dark transition-colors hover:bg-primary-subtle focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary motion-reduce:transition-none">Back to welcome</Link>
      </header>

      <main className="mx-auto grid w-full max-w-7xl items-center gap-10 px-4 pb-16 pt-6 sm:px-6 sm:pt-10 lg:min-h-[calc(100svh-7rem)] lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] lg:gap-16 lg:px-8 lg:pb-24">
        <div className="max-w-xl">
          <p className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-surface-card px-4 py-2 text-xs font-extrabold uppercase tracking-brand text-primary-dark shadow-subtle">
            <span className="size-2 rounded-full bg-coral" aria-hidden="true" />
            Welcome back
          </p>
          <h1 className="mt-6 text-4xl font-extrabold leading-tight tracking-tight text-text-strong sm:text-5xl">Find your focus again.</h1>
          <p className="mt-5 max-w-lg text-base leading-8 text-text-muted sm:text-lg">Log in to pick up where your study plan left off.</p>

          <div className="mt-10 hidden max-w-md -rotate-2 rounded-3xl border border-primary/20 bg-primary-subtle p-5 shadow-card lg:block" aria-hidden="true">
            <div className="rotate-2 rounded-2xl border border-primary/20 bg-surface-card p-5 shadow-subtle">
              <div className="flex items-center justify-between border-b border-dashed border-border pb-4">
                <span className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">Your next session</span>
                <span className="size-3 rounded-full bg-accent" />
              </div>
              <div className="mt-5 rounded-xl border-l-4 border-primary bg-cream p-4">
                <p className="text-sm font-extrabold text-text-strong">One clear step at a time</p>
                <p className="mt-1 text-xs text-text-muted">Your study space is ready when you are.</p>
              </div>
              <div className="mt-4 flex items-center gap-2">
                <span className="size-3 rounded-full bg-primary" />
                <span className="h-2 flex-1 rounded-full bg-primary-subtle" />
                <span className="h-2 w-12 rounded-full bg-accent-light" />
              </div>
            </div>
          </div>
        </div>

        <section className="min-w-0 rounded-3xl border border-primary/15 bg-surface-card p-5 shadow-card sm:p-8 lg:p-10" aria-labelledby="login-title">
          {isSignedIn ? (
            <div ref={successRef} tabIndex={-1} role="status" className="py-8 text-center outline-none">
              <span className="mx-auto flex size-16 items-center justify-center rounded-full bg-success-subtle text-3xl font-extrabold text-success" aria-hidden="true">✓</span>
              <h2 id="login-title" className="mt-5 text-3xl font-extrabold text-text-strong">You’re logged in.</h2>
              <p className="mx-auto mt-3 max-w-md leading-7 text-text-muted">Welcome back to StudyOps.</p>
              <Link to="/app" className="mt-7 inline-flex min-h-12 items-center justify-center rounded-xl bg-accent px-7 font-extrabold text-text-strong shadow-accent-glow transition-colors hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary motion-reduce:transition-none">Open dashboard</Link>
            </div>
          ) : (
            <>
              <div className="border-b border-dashed border-border pb-6">
                <h2 id="login-title" className="text-2xl font-extrabold text-text-strong sm:text-3xl">Log in to your account</h2>
                <p className="mt-2 text-sm leading-6 text-text-muted">Your subjects, tasks, and study sessions are waiting.</p>
              </div>

              {searchParams.get('registered') === '1' ? (
                <p role="status" className="mt-6 rounded-xl border border-success/25 bg-success-subtle px-4 py-3 text-sm font-semibold text-text-strong">Account created. Log in to continue.</p>
              ) : null}

              <fetcher.Form method="post" ref={formRef} noValidate aria-busy={isSubmitting} className="mt-7 space-y-6">
                {errors?.formErrors.length ? (
                  <div data-error-summary tabIndex={-1} role="alert" className="rounded-xl border border-coral/35 bg-coral/10 p-4 text-sm font-medium text-error-dark outline-none focus-visible:ring-3 focus-visible:ring-coral/40">
                    {errors.formErrors.map((message) => <p key={message}>{message}</p>)}
                  </div>
                ) : null}

                <RegistrationField name="username" label="Username" autoComplete="username" error={errors?.fieldErrors.username?.[0]} />
                <RegistrationField name="password" label="Password" type="password" autoComplete="current-password" error={errors?.fieldErrors.password?.[0]} />

                <button type="submit" disabled={isSubmitting} className="flex min-h-13 w-full items-center justify-center rounded-xl bg-accent px-7 py-3.5 text-base font-extrabold text-text-strong shadow-accent-glow transition duration-200 hover:-translate-y-0.5 hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:translate-y-0 active:bg-accent-dark disabled:opacity-60 motion-reduce:transform-none motion-reduce:transition-none">
                  {isSubmitting ? 'Logging in…' : 'Log in'}
                </button>
                <p className="text-center text-sm text-text-muted">New to StudyOps? <Link to="/register" className="font-bold text-primary-dark underline underline-offset-4 hover:text-text-strong focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary">Create an account</Link></p>
              </fetcher.Form>
            </>
          )}
        </section>
      </main>
    </div>
  )
}
