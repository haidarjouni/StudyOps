import { useEffect } from 'react'
import { useLoaderData } from 'react-router'
import { PageHeading } from '../../components/DashboardParts'
import { SubjectForm } from '../../components/SubjectForm'
import type { subjectLoader } from './loaders'
export function SubjectEditPage() { const { subject } = useLoaderData<typeof subjectLoader>(); useEffect(() => { document.title = `Edit ${subject.name} | StudyOps` }, [subject.name]); return <><PageHeading title="Edit subject" description={`Update ${subject.name}.`} /><SubjectForm subject={subject} /></> }
