export type TaskType = 'assignment' | 'exam' | 'study' | 'other'
export type TaskStatus = 'todo' | 'in_progress' | 'done' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high'
export type Task = { id: number; user: number; subject: number; title: string; description: string; task_type: TaskType; task_status: TaskStatus; task_priority: TaskPriority; estimated_minutes: number; due_date: string; created_at: string; updated_at: string }
export type TaskInput = Pick<Task, 'subject' | 'title' | 'description' | 'task_type' | 'task_status' | 'task_priority' | 'estimated_minutes' | 'due_date'>
