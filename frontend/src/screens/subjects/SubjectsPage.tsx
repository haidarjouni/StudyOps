import { useEffect } from 'react'
import { Form, Link, useLoaderData, useSearchParams } from 'react-router'
import { card, EmptyState, input, PageHeading, secondary } from '../../components/DashboardParts'
import type { subjectsLoader } from './loaders'
export function SubjectsPage() {
  const { subjects } = useLoaderData<typeof subjectsLoader>()
  const [params] = useSearchParams()
  const query = params.get('q')?.trim().toLowerCase() ?? ''
  const visible = subjects.filter(subject => `${subject.name} ${subject.code} ${subject.semester}`.toLowerCase().includes(query))
  useEffect(() => { document.title = 'Subjects | StudyOps' }, [])
  return <><PageHeading title="Subjects" description="Keep every course and semester in one place." addTo="/app/subjects/new" addLabel="Add subject" />{params.get('deleted') === '1' && <p role="status" className="mb-5 rounded-xl bg-success-subtle p-4 font-semibold text-success">Subject deleted.</p>}
    <Form method="get" className="mb-6 max-w-lg"><label htmlFor="subject-search" className="mb-2 block text-sm font-bold">Search your subjects</label><div className="flex gap-2"><input id="subject-search" name="q" defaultValue={params.get('q') ?? ''} placeholder="Name, code, or semester" className={input} /><button className={secondary}>Search</button></div></Form>
    {visible.length ? <ul className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{visible.map(subject => <li key={subject.id} className={`${card} border-l-4 border-l-primary`}><p className="text-xs font-extrabold uppercase tracking-brand text-primary-dark">{subject.code} · Semester {subject.semester}</p><h2 className="mt-3 text-xl font-extrabold">{subject.name}</h2><div className="mt-5 flex gap-3"><Link to={`/app/subjects/${subject.id}`} className={secondary}>View subject</Link><Link to={`/app/subjects/${subject.id}/edit`} className="self-center font-bold text-primary-dark underline underline-offset-4 focus-visible:outline-3 focus-visible:outline-primary">Edit</Link></div></li>)}</ul> : <EmptyState title={query ? 'No subjects match your search' : 'No subjects yet'} description={query ? 'Try a different name, code, or semester.' : 'Add your first subject to organize tasks and study sessions.'} to={query ? '/app/subjects' : '/app/subjects/new'} action={query ? 'Clear search' : 'Add subject'} />}</>
}
