import { useEffect } from 'react'
import { useLoaderData } from 'react-router'
import { EmptyState, PageHeading } from '../../components/DashboardParts'
import { SessionForm } from '../../components/SessionForm'
import type { sessionFormLoader } from './loaders'
export function SessionCreatePage() { const { subjects, tasks } = useLoaderData<typeof sessionFormLoader>(); useEffect(() => { document.title = 'Schedule session | StudyOps' }, []); return <><PageHeading title="Schedule a session" description="Reserve a focused block for your studies." />{subjects.length ? <SessionForm session={null} subjects={subjects} tasks={tasks} /> : <EmptyState title="Add a subject first" description="Every session belongs to a subject." to="/app/subjects/new" action="Add subject" />}</> }
