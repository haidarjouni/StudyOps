import { useEffect, useRef } from 'react'
import { Form, Link, useActionData, useNavigation } from 'react-router'
import { RegistrationField } from '../../components/RegistrationField'
import type { registrationAction } from './actions'

function localTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
}

export function RegistrationPage() {
  const actionData = useActionData<typeof registrationAction>()
  const navigation = useNavigation()
  const formRef = useRef<HTMLFormElement>(null)
  const isSubmitting = navigation.state === 'submitting'
  const errors = actionData?.ok === false ? actionData.errors : undefined
  const fieldErrors = errors?.fieldErrors
  useEffect(() => {
    document.title = 'Create your account | StudyOps'
  }, [])

  useEffect(() => {
    if (!errors) return
    // focus on the first invalid field or the error summary if there are errors
    const invalidField = formRef.current?.querySelector<HTMLInputElement>('[aria-invalid="true"]')
    // focus on the first invalid field or the error summary if there are errors
    const summary = formRef.current?.querySelector<HTMLDivElement>('[data-error-summary]')
    ;(invalidField || summary)?.focus()
  }, [errors])

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

      <main className="mx-auto grid w-full max-w-7xl gap-10 px-4 pb-16 pt-6 sm:px-6 sm:pt-10 lg:grid-cols-[minmax(0,0.8fr)_minmax(0,1.2fr)] lg:items-start lg:gap-16 lg:px-8 lg:pb-24 lg:pt-16">
        <div className="max-w-xl lg:sticky lg:top-10">
          <p className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-surface-card px-4 py-2 text-xs font-extrabold uppercase tracking-brand text-primary-dark shadow-subtle">
            <span className="size-2 rounded-full bg-coral" aria-hidden="true" />
            Start studying your way
          </p>
          <h1 className="mt-6 text-4xl font-extrabold leading-tight tracking-tight text-text-strong sm:text-5xl">Make a plan that fits your life.</h1>
          <p className="mt-5 max-w-lg text-base leading-8 text-text-muted sm:text-lg">Create your StudyOps account and tell us when you prefer to study. You can adjust these preferences later.</p>
          <div className="mt-8 hidden rounded-3xl border border-primary/20 bg-primary-subtle p-6 shadow-card lg:block" aria-hidden="true">
            <div className="rotate-[-2deg] rounded-2xl border border-primary/20 bg-surface-card p-5 shadow-subtle">
              <div className="flex items-center justify-between border-b border-dashed border-border pb-3">
                <span className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">Your study rhythm</span>
                <span className="size-3 rounded-full bg-accent" />
              </div>
              <div className="mt-4 flex items-center gap-3 rounded-xl bg-cream p-3">
                <span className="flex size-10 items-center justify-center rounded-xl bg-accent text-lg" aria-hidden="true">✦</span>
                <div><p className="text-sm font-extrabold text-text-strong">Focused sessions</p><p className="text-xs text-text-muted">At the times that work for you</p></div>
              </div>
              <div className="mt-3 flex items-center gap-3 rounded-xl bg-sky-subtle p-3">
                <span className="flex size-10 items-center justify-center rounded-xl bg-sky text-surface-card" aria-hidden="true">✓</span>
                <div><p className="text-sm font-extrabold text-text-strong">Room to reset</p><p className="text-xs text-text-muted">Breaks built into the plan</p></div>
              </div>
            </div>
          </div>
        </div>

        <section className="min-w-0 rounded-3xl border border-primary/15 bg-surface-card p-5 shadow-card sm:p-8 lg:p-10" aria-labelledby="registration-title">
              <div className="border-b border-dashed border-border pb-6">
                <h2 id="registration-title" className="text-2xl font-extrabold text-text-strong sm:text-3xl">Create your account</h2>
                <p className="mt-2 text-sm leading-6 text-text-muted">A few details now will make your first plan feel like yours.</p>
              </div>
                {/* This is the form for creating a new user account */}
              <Form method="post" ref={formRef} noValidate aria-busy={isSubmitting} className="mt-7 space-y-8">
                {/* checks for form wide errors not specific fields */}
                {errors?.formErrors.length ? (
                  <div data-error-summary tabIndex={-1} role="alert" className="rounded-xl border border-coral/35 bg-coral/10 p-4 text-sm font-medium text-error-dark outline-none focus-visible:ring-3 focus-visible:ring-coral/40">
                    {errors.formErrors.map((message) => <p key={message}>{message}</p>)}
                  </div>
                ) : null}

                <fieldset className="space-y-5">
                  <legend className="mb-5 text-lg font-extrabold text-text-strong">Your details</legend>
                  <div className="grid gap-5 sm:grid-cols-2">
                    <RegistrationField name="username" label="Username" autoComplete="username" maxLength={150} hint="This is how you’ll sign in." error={fieldErrors?.username?.[0]} />
                    <RegistrationField name="email" label="Email address" type="email" autoComplete="email" error={fieldErrors?.email?.[0]} />
                    <RegistrationField name="password" label="Password" type="password" autoComplete="new-password" hint="Use a password you haven’t used elsewhere." error={fieldErrors?.password?.[0]} />
                    <RegistrationField name="confirm_password" label="Confirm password" type="password" autoComplete="new-password" error={fieldErrors?.confirm_password?.[0]} />
                  </div>
                </fieldset>

                <fieldset className="space-y-5 border-t border-dashed border-border pt-7">
                  <legend className="text-lg font-extrabold text-text-strong">Your study preferences</legend>
                  <p className="text-sm leading-6 text-text-muted">Set your usual study window and pace. All times are in your chosen time zone.</p>
                  <RegistrationField name="timezone" label="Time zone" autoComplete="off" defaultValue={localTimezone()} maxLength={64} hint="Use an IANA name, such as Asia/Beirut." error={fieldErrors?.timezone?.[0]} />
                  <div className="grid gap-5 sm:grid-cols-2">
                    <RegistrationField name="earliest_study_time" label="Earliest study time" type="time" defaultValue="08:00" error={fieldErrors?.earliest_study_time?.[0]} />
                    <RegistrationField name="latest_study_time" label="Latest study time" type="time" defaultValue="21:30" error={fieldErrors?.latest_study_time?.[0]} />
                    <RegistrationField name="preferred_session_minutes" label="Session length (minutes)" type="number" min={1} defaultValue={45} error={fieldErrors?.preferred_session_minutes?.[0]} />
                    <RegistrationField name="buffer_minutes" label="Break between sessions (minutes)" type="number" min={0} defaultValue={10} error={fieldErrors?.buffer_minutes?.[0]} />
                  </div>
                </fieldset>

                <div className="border-t border-dashed border-border pt-7">
                  <button type="submit" disabled={isSubmitting} className="flex min-h-13 w-full items-center justify-center rounded-xl bg-accent px-7 py-3.5 text-base font-extrabold text-text-strong shadow-accent-glow transition duration-200 hover:-translate-y-0.5 hover:bg-accent-light focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary active:translate-y-0 active:bg-accent-dark disabled:opacity-60 motion-reduce:transform-none motion-reduce:transition-none">
                    {isSubmitting ? 'Creating account…' : 'Create account'}
                  </button>
                  <p className="mt-4 text-center text-sm text-text-muted">Already have an account? <Link to="/login" className="font-bold text-primary-dark underline underline-offset-4 hover:text-text-strong focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-primary">Log in</Link></p>
                </div>
              </Form>
        </section>
      </main>
    </div>
  )
}
