import { useEffect, useRef, useState } from 'react'
import { Form, NavLink, Outlet, useFetcher, useLoaderData, useLocation, useNavigation, useRevalidator } from 'react-router'
import type { createThreadAction } from '../screens/assistant/actions'
import type { dashboardLoader } from '../screens/overview/loaders'

const links = [
  { to: '/app', label: 'Overview', end: true },
  { to: '/app/subjects', label: 'Subjects' },
  { to: '/app/tasks', label: 'Tasks' },
  { to: '/app/study-sessions', label: 'Study sessions' },
  { to: '/app/preferences', label: 'Preferences' },
]

export function DashboardLayout() {
  const { user, threads, threadsError } = useLoaderData<typeof dashboardLoader>()
  const location = useLocation()
  const [openAtPath, setOpenAtPath] = useState<string | null>(null)
  const open = openAtPath === location.pathname
  const [assistantOpen, setAssistantOpen] = useState(() => location.pathname.startsWith('/app/assistant/'))
  const createFetcher = useFetcher<typeof createThreadAction>()
  const isCreating = createFetcher.state !== 'idle'
  const createError = !isCreating && createFetcher.data?.ok === false ? createFetcher.data.message : null
  const errorRef = useRef<HTMLParagraphElement>(null)
  const isAssistant = location.pathname.startsWith('/app/assistant/')
  const navigation = useNavigation()
  const revalidator = useRevalidator()
  const sortedThreads = threads?.slice().sort((a, b) => b.created_at.localeCompare(a.created_at))

  useEffect(() => {
    if (createError) errorRef.current?.focus()
  }, [createError])

  return <div className="min-h-svh bg-surface-base text-text-strong lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
    <a href="#main-content" className="sr-only rounded-xl bg-accent px-4 py-3 font-bold focus:not-sr-only focus:absolute focus:z-50 focus:m-3">Skip to content</a>
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-surface-card px-4 py-3 shadow-subtle lg:hidden">
      <NavLink to="/app" className="text-xl font-extrabold tracking-tight focus-visible:outline-3 focus-visible:outline-primary">Study<span className="text-primary-dark">Ops</span></NavLink>
      <button type="button" aria-expanded={open} aria-controls="mobile-nav" onClick={() => setOpenAtPath(open ? null : location.pathname)} className="min-h-11 rounded-xl border border-border px-4 font-bold focus-visible:outline-3 focus-visible:outline-primary">{open ? 'Close menu' : 'Menu'}</button>
    </header>
    <aside id="mobile-nav" className={`${open ? 'block' : 'hidden'} z-20 border-b border-primary-dark bg-primary-dark px-4 py-5 text-white lg:sticky lg:top-0 lg:block lg:h-svh lg:overflow-y-auto lg:border-r lg:border-b-0 lg:px-5 lg:py-8`}>
      <NavLink to="/app" className="hidden items-center gap-3 rounded-xl text-2xl font-extrabold tracking-tight focus-visible:outline-3 focus-visible:outline-accent lg:flex"><span className="flex size-11 items-center justify-center rounded-xl bg-accent text-primary-dark">S</span>StudyOps</NavLink>
      <p className="mt-2 hidden text-sm text-white/80 lg:block">A clearer place to study.</p>
      <nav aria-label="Main navigation" className="grid gap-1 lg:mt-12">
        {links.map(link => 
            <NavLink key={link.to} to={link.to} end={link.end} onClick={() => setOpenAtPath(null)} className={({ isActive }) => `flex min-h-11 items-center rounded-xl px-4 text-sm font-bold transition-colors focus-visible:outline-3 focus-visible:outline-accent ${isActive ? 'bg-cream text-primary-dark shadow-subtle' : 'text-white hover:bg-white/15'}`}>
                {link.label}
            </NavLink>
        )}
        <div>
          <button type="button" aria-expanded={assistantOpen} aria-controls="assistant-menu" onClick={() => setAssistantOpen(!assistantOpen)} className={`flex min-h-11 w-full items-center justify-between rounded-xl px-4 text-left text-sm font-bold transition-colors focus-visible:outline-3 focus-visible:outline-accent ${isAssistant ? 'bg-cream text-primary-dark shadow-subtle' : 'text-white hover:bg-white/15'}`}>
            <span>Assistant</span>
            <svg aria-hidden="true" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`size-4 transition-transform motion-reduce:transition-none ${assistantOpen ? 'rotate-180' : ''}`}><path d="m5 7.5 5 5 5-5" /></svg>
          </button>
          {assistantOpen && <div id="assistant-menu" className="ml-4 mt-2 border-l border-white/30 pl-3">
            <createFetcher.Form method="post" action="/app/assistant/new" aria-busy={isCreating}>
              <button type="submit" disabled={isCreating} className="inline-flex min-h-11 items-center rounded-lg text-xs font-bold focus-visible:outline-3 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-60">
                <span className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-2 text-text-strong transition-colors hover:bg-accent-light motion-reduce:transition-none">
                  <span aria-hidden="true" className="text-base leading-none">+</span>
                  {isCreating ? 'Creating chat…' : 'New chat'}
                </span>
              </button>
            </createFetcher.Form>
            {createError && <p ref={errorRef} tabIndex={-1} role="alert" className="mt-2 rounded-xl border border-coral-light bg-cream px-3 py-2 text-sm font-semibold text-error-dark outline-none focus-visible:ring-3 focus-visible:ring-accent">{createError}</p>}
            <p className="mt-4 px-2 text-xs font-bold uppercase tracking-wide text-white/80">Your chats</p>
            {threadsError ? (
              <div role="alert" className="mt-2 rounded-lg bg-white/10 px-3 py-3 text-xs text-white">
                <p>Couldn’t load your chats.</p>
                <button type="button" disabled={revalidator.state !== 'idle'} onClick={() => revalidator.revalidate()} className="mt-2 min-h-11 font-bold underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-accent disabled:opacity-60">{revalidator.state !== 'idle' ? 'Retrying…' : 'Try again'}</button>
              </div>
            ) : sortedThreads?.length ? (
              <ul aria-label="Your chats" className="mt-2 max-h-72 space-y-1 overflow-y-auto pr-1">
                {sortedThreads.map(thread => <li key={thread.id}>
                  <NavLink to={`/app/assistant/${thread.id}`} onClick={() => setOpenAtPath(null)} className={({ isActive }) => `flex min-h-11 min-w-0 flex-col justify-center rounded-lg px-3 py-2 transition-colors focus-visible:outline-3 focus-visible:outline-accent ${isActive ? 'bg-white/20 text-white' : 'text-white/90 hover:bg-white/10'}`}>
                    <span className="truncate text-sm font-semibold">{thread.title || 'New chat'}</span>
                    <span className="text-xs text-white/75">{new Date(thread.created_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</span>
                  </NavLink>
                </li>)}
              </ul>
            ) : (
              <p className="mt-2 px-2 text-xs text-white/80">No chats yet.</p>
            )}
          </div>}
        </div>
      </nav>
      <div className="mt-6 border-t border-white/25 pt-5 lg:mt-12">
        <p className="truncate px-4 text-sm font-bold">{user.username}</p>
        <Form action="/app/logout" method="post"><button type="submit" className="mt-2 min-h-11 w-full rounded-xl px-4 text-left text-sm font-bold text-white hover:bg-white/15 focus-visible:outline-3 focus-visible:outline-accent">Log out</button></Form>
      </div>
    </aside>
    <main id="main-content" className="min-w-0 px-4 py-7 sm:px-6 lg:px-8 lg:py-10">
        <div className="mx-auto max-w-7xl">
            {navigation.state === 'loading' && 
                <p role="status" className="mb-4 rounded-xl bg-primary-subtle px-4 py-2 text-sm font-bold text-primary-dark">
                    Loading…
                </p>
            } <Outlet />
        </div>
    </main>
  </div>
}
