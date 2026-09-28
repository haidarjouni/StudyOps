import { apiRequest } from '../../lib/api'
import type { Subject, SubjectInput } from '../../types/subjects'
export const listSubjects = () => apiRequest<Subject[]>('/api/subject/')
export const getSubject = (id: string) => apiRequest<Subject>(`/api/subject/${id}/`)
export const createSubject = (input: SubjectInput) => apiRequest<Subject>('/api/subject/', 'POST', input)
export const updateSubject = (id: string, input: SubjectInput) => apiRequest<Subject>(`/api/subject/${id}/`, 'PATCH', input)
export const deleteSubject = (id: string) => apiRequest<void>(`/api/subject/${id}/`, 'DELETE')
