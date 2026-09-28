import type { LoaderFunctionArgs } from 'react-router'
import { listSubjects } from '../subjects/service'
import { listTasks } from '../tasks/service'
import { getSession, listSessions } from './service'
export async function sessionsLoader({ request }: LoaderFunctionArgs) {
  const source = new URL(request.url).searchParams
  const filters = new URLSearchParams()
  for (const key of ['subject', 'task', 'status']) if (source.get(key)) filters.set(key, source.get(key)!)
  const [sessions, subjects, tasks] = await Promise.all([listSessions(filters.size ? `?${filters}` : ''), listSubjects(), listTasks()])
  return { sessions, subjects, tasks }
}
export async function sessionFormLoader({ params }: LoaderFunctionArgs) {
  const [subjects, tasks, session] = await Promise.all([listSubjects(), listTasks(), params.id ? getSession(params.id) : Promise.resolve(null)])
  return { subjects, tasks, session }
}
export async function sessionLoader({ params }: LoaderFunctionArgs) { return { session: await getSession(params.id!) } }
