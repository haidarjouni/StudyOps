import { useEffect } from 'react'
import { useLoaderData } from 'react-router'
import { EmptyState, PageHeading } from '../../components/DashboardParts'
import { TaskForm } from '../../components/TaskForm'
import type { taskFormLoader } from './loaders'
export function TaskCreatePage() { const { subjects } = useLoaderData<typeof taskFormLoader>(); useEffect(() => { document.title = 'Add task | StudyOps' }, []); return <><PageHeading title="Add task" description="Turn study work into a clear next step." />{subjects.length ? <TaskForm task={null} subjects={subjects} /> : <EmptyState title="Add a subject first" description="Every task belongs to a subject." to="/app/subjects/new" action="Add subject" />}</> }
