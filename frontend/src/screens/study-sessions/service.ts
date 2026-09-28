import { apiRequest } from '../../lib/api'
import type { StudySession, SessionInput } from '../../types/sessions'
export const listSessions = (search = '') => apiRequest<StudySession[]>(`/api/study_session/${search}`)
export const getSession = (id: string) => apiRequest<StudySession>(`/api/study_session/${id}/`)
export const createSession = (input: SessionInput) => apiRequest<StudySession>('/api/study_session/', 'POST', input)
export const updateSession = (id: string, input: Partial<SessionInput>) => apiRequest<StudySession>(`/api/study_session/${id}/`, 'PATCH', input)
export const deleteSession = (id: string) => apiRequest<void>(`/api/study_session/${id}/`, 'DELETE')
