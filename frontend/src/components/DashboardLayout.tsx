import { useState } from 'react'
import { Form, NavLink, Outlet, useLoaderData, useNavigation } from 'react-router'
import type { dashboardLoader } from '../screens/overview/loaders'

const links = [
  { to: '/app', label: 'Overview', end: true },
  { to: '/app/subjects', label: 'Subjects' },
  { to: '/app/tasks', label: 'Tasks' },
  { to: '/app/study-sessions', label: 'Study sessions' },
  { to: '/app/preferences', label: 'Preferences' },
]

export function DashboardLayout() {
  const { user } = useLoaderData<typeof dashboardLoader>()
  const [open, setOpen] = useState(false)
  const navigation = useNavigation()
  return <div className="min-h-svh bg-surface-base text-text-strong lg:grid lg:grid-cols-[16rem_minmax(0,1fr)]">
    <a href="#main-content" className="sr-only rounded-xl bg-accent px-4 py-3 font-bold focus:not-sr-only focus:absolute focus:z-50 focus:m-3">Skip to content</a>
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-surface-card px-4 py-3 shadow-subtle lg:hidden">
      <NavLink to="/app" className="text-xl font-extrabold tracking-tight focus-visible:outline-3 focus-visible:outline-primary">Study<span className="text-primary-dark">Ops</span></NavLink>
      <button type="button" aria-expanded={open} aria-controls="mobile-nav" onClick={() => setOpen(!open)} className="min-h-11 rounded-xl border border-border px-4 font-bold focus-visible:outline-3 focus-visible:outline-primary">{open ? 'Close menu' : 'Menu'}</button>
    </header>
    <aside id="mobile-nav" className={`${open ? 'block' : 'hidden'} z-20 border-b border-primary-dark bg-primary-dark px-4 py-5 text-white lg:sticky lg:top-0 lg:block lg:h-svh lg:border-r lg:border-b-0 lg:px-5 lg:py-8`}>
      <NavLink to="/app" className="hidden items-center gap-3 rounded-xl text-2xl font-extrabold tracking-tight focus-visible:outline-3 focus-visible:outline-accent lg:flex"><span className="flex size-11 items-center justify-center rounded-xl bg-accent text-primary-dark">S</span>StudyOps</NavLink>
      <p className="mt-2 hidden text-sm text-white/80 lg:block">A clearer place to study.</p>
      <nav aria-label="Main navigation" className="grid gap-1 lg:mt-12">
        {links.map(link => <NavLink key={link.to} to={link.to} end={link.end} onClick={() => setOpen(false)} className={({ isActive }) => `flex min-h-11 items-center rounded-xl px-4 text-sm font-bold transition-colors focus-visible:outline-3 focus-visible:outline-accent ${isActive ? 'bg-cream text-primary-dark shadow-subtle' : 'text-white hover:bg-white/15'}`}>{link.label}</NavLink>)}
      </nav>
      <div className="mt-6 border-t border-white/25 pt-5 lg:mt-12">
        <p className="truncate px-4 text-sm font-bold">{user.username}</p>
        <Form action="/app/logout" method="post"><button type="submit" className="mt-2 min-h-11 w-full rounded-xl px-4 text-left text-sm font-bold text-white hover:bg-white/15 focus-visible:outline-3 focus-visible:outline-accent">Log out</button></Form>
      </div>
    </aside>
    <main id="main-content" className="min-w-0 px-4 py-7 sm:px-6 lg:px-8 lg:py-10"><div className="mx-auto max-w-7xl">{navigation.state === 'loading' && <p role="status" className="mb-4 rounded-xl bg-primary-subtle px-4 py-2 text-sm font-bold text-primary-dark">Loading…</p>}<Outlet /></div></main>
  </div>
}
