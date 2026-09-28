import { useEffect } from 'react'
import { Form, Link, useLoaderData, useNavigation, useSearchParams } from 'react-router'
import { card, danger, PageHeading, secondary } from '../../components/DashboardParts'
import type { taskLoader } from './loaders'
export function TaskDetailPage() {
  const { task, subjects } = useLoaderData<typeof taskLoader>()
  const [params] = useSearchParams()
  const navigation = useNavigation()
  useEffect(() => { document.title = `${task.title} | StudyOps` }, [task.title])
  function handleDelete(event: React.FormEvent<HTMLFormElement>) { if (!window.confirm(`Delete ${task.title}? Linked sessions will remain without a task.`)) event.preventDefault() }
  return <><PageHeading title={task.title} description={`${subjects.find(subject => subject.id === task.subject)?.name ?? 'Subject'} · ${task.task_type}`} />{params.get('saved') === '1' && <p role="status" className="mb-5 rounded-xl bg-success-subtle p-4 font-semibold text-success">Task saved.</p>}<div className={`${card} max-w-3xl`}><p className="whitespace-pre-wrap leading-7">{task.description}</p><dl className="mt-6 grid gap-4 border-t border-dashed border-border pt-5 sm:grid-cols-2"><div><dt className="text-sm text-text-muted">Due</dt><dd className="font-bold">{new Intl.DateTimeFormat(undefined, { dateStyle: 'full', timeStyle: 'short' }).format(new Date(task.due_date))}</dd></div><div><dt className="text-sm text-text-muted">Estimate</dt><dd className="font-bold">{task.estimated_minutes} minutes</dd></div><div><dt className="text-sm text-text-muted">Status</dt><dd className="font-bold capitalize">{task.task_status.replace('_', ' ')}</dd></div><div><dt className="text-sm text-text-muted">Priority</dt><dd className="font-bold capitalize">{task.task_priority}</dd></div></dl><div className="mt-8 flex flex-wrap gap-3"><Link to={`/app/tasks/${task.id}/edit`} className={secondary}>Edit task</Link><Form method="post" action={`/app/tasks/${task.id}/delete`} onSubmit={handleDelete}><button disabled={navigation.state === 'submitting'} className={danger}>Delete task</button></Form></div></div></>
}
