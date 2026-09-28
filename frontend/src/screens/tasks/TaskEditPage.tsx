import { useEffect } from 'react'
import { useLoaderData } from 'react-router'
import { PageHeading } from '../../components/DashboardParts'
import { TaskForm } from '../../components/TaskForm'
import type { taskFormLoader } from './loaders'
export function TaskEditPage() { const { subjects, task } = useLoaderData<typeof taskFormLoader>(); useEffect(() => { document.title = `Edit task | StudyOps` }, []); return <><PageHeading title="Edit task" description={task?.title ?? ''} /><TaskForm task={task} subjects={subjects} /></> }
