import { useEffect } from 'react'
import { Form, Link, useLoaderData, useNavigation, useSearchParams } from 'react-router'
import { card, danger, PageHeading, secondary } from '../../components/DashboardParts'
import type { subjectLoader } from './loaders'
export function SubjectDetailPage() {
  const { subject } = useLoaderData<typeof subjectLoader>()
  const [params] = useSearchParams()
  const navigation = useNavigation()
  useEffect(() => { document.title = `${subject.name} | StudyOps` }, [subject.name])
  function handleDelete(event: React.FormEvent<HTMLFormElement>) { if (!window.confirm(`Delete ${subject.name}? Its tasks and study sessions will also be deleted.`)) event.preventDefault() }
  return <><PageHeading title={subject.name} description={`${subject.code} · Semester ${subject.semester}`} />{params.get('saved') === '1' && <p role="status" className="mb-5 rounded-xl bg-success-subtle p-4 font-semibold text-success">Subject saved.</p>}<div className={`${card} max-w-2xl`}><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm font-bold text-text-muted">Code</dt><dd className="mt-1 text-lg font-bold">{subject.code}</dd></div><div><dt className="text-sm font-bold text-text-muted">Semester</dt><dd className="mt-1 text-lg font-bold">{subject.semester}</dd></div></dl><div className="mt-8 flex flex-wrap gap-3"><Link to={`/app/subjects/${subject.id}/edit`} className={secondary}>Edit subject</Link><Form method="post" action={`/app/subjects/${subject.id}/delete`} onSubmit={handleDelete}><button disabled={navigation.state === 'submitting'} className={danger}>{navigation.state === 'submitting' ? 'Deleting…' : 'Delete subject'}</button></Form></div><p className="mt-4 text-sm text-text-muted">Deleting this subject also deletes its tasks and sessions.</p></div></>
}
