import type { LoaderFunctionArgs } from 'react-router'
import { getSubject, listSubjects } from './service'
export async function subjectsLoader() { return { subjects: await listSubjects() } }
export async function subjectLoader({ params }: LoaderFunctionArgs) { return { subject: await getSubject(params.id!) } }
