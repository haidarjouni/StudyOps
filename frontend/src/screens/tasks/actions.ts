import { data, redirect, type ActionFunctionArgs } from 'react-router'
import * as z from 'zod'
import { formErrors, isoValue, numberValue, value } from '../../lib/api'
import type { TaskInput } from '../../types/tasks'
import { createTask, deleteTask, updateTask } from './service'
const schema: z.ZodType<TaskInput> = z.strictObject({
  subject: z.number().int().positive('Choose a subject.'), title: z.string().min(1, 'Enter a title.').max(100), description: z.string().min(1, 'Enter a description.'),
  task_type: z.enum(['assignment', 'exam', 'study', 'other']), task_status: z.enum(['todo', 'in_progress', 'done', 'cancelled']), task_priority: z.enum(['low', 'medium', 'high']),
  estimated_minutes: z.number().int().positive('Enter a positive number of minutes.'), due_date: z.iso.datetime({ message: 'Choose a due date.' }),
})
async function save({ request, params }: ActionFunctionArgs, edit: boolean) {
  const form = await request.formData()
  const parsed = schema.safeParse({ subject: numberValue(form, 'subject'), title: value(form, 'title'), description: value(form, 'description'), task_type: value(form, 'task_type'), task_status: value(form, 'task_status'), task_priority: value(form, 'task_priority'), estimated_minutes: numberValue(form, 'estimated_minutes'), due_date: isoValue(value(form, 'due_date')) })
  if (!parsed.success) return data({ ok: false as const, errors: z.flattenError(parsed.error) }, { status: 400 })
  try { const task = edit ? await updateTask(params.id!, parsed.data) : await createTask(parsed.data); return redirect(`/app/tasks/${task.id}?saved=1`) }
  catch (error) { return data({ ok: false as const, errors: formErrors(error) }, { status: 400 }) }
}
export const createTaskAction = (args: ActionFunctionArgs) => save(args, false)
export const editTaskAction = (args: ActionFunctionArgs) => save(args, true)
export async function deleteTaskAction({ params }: ActionFunctionArgs) { await deleteTask(params.id!); return redirect('/app/tasks?deleted=1') }
