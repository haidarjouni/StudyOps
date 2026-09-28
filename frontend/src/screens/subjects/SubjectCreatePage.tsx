import { useEffect } from 'react'
import { PageHeading } from '../../components/DashboardParts'
import { SubjectForm } from '../../components/SubjectForm'
export function SubjectCreatePage() { useEffect(() => { document.title = 'Add subject | StudyOps' }, []); return <><PageHeading title="Add subject" description="Give your course a clear name and code." /><SubjectForm /></> }
