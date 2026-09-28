import { apiRequest } from '../../lib/api'
import type { Task, TaskInput } from '../../types/tasks'
export const listTasks = (search = '') => apiRequest<Task[]>(`/api/study_task/${search}`)
export const getTask = (id: string) => apiRequest<Task>(`/api/study_task/${id}/`)
export const createTask = (input: TaskInput) => apiRequest<Task>('/api/study_task/', 'POST', input)
export const updateTask = (id: string, input: TaskInput) => apiRequest<Task>(`/api/study_task/${id}/`, 'PATCH', input)
export const deleteTask = (id: string) => apiRequest<void>(`/api/study_task/${id}/`, 'DELETE')
