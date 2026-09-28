import { data, type ActionFunctionArgs } from 'react-router'
import * as z from 'zod'
import { formErrors, numberValue, value } from '../../lib/api'
import type { Preferences } from '../../types/preferences'
import { updatePreferences } from './service'
const time = z.string().regex(/^([01]\d|2[0-3]):[0-5]\d:00$/, 'Enter a valid time.')
const schema: z.ZodType<Preferences> = z.strictObject({ timezone: z.string().min(1, 'Enter a timezone.').max(64).refine(zone => { try { new Intl.DateTimeFormat('en', { timeZone: zone }); return true } catch { return false } }, 'Enter a valid IANA timezone.'), earliest_study_time: time, latest_study_time: time, preferred_session_minutes: z.number().int().positive('Enter a positive number.'), buffer_minutes: z.number().int().nonnegative('Enter zero or a positive number.') }).refine(v => v.earliest_study_time < v.latest_study_time, { path: ['latest_study_time'], message: 'End time must be after start time.' })
export async function preferencesAction({ request }: ActionFunctionArgs) {
  const form = await request.formData()
  const parsed = schema.safeParse({ timezone: value(form, 'timezone'), earliest_study_time: `${value(form, 'earliest_study_time')}:00`, latest_study_time: `${value(form, 'latest_study_time')}:00`, preferred_session_minutes: numberValue(form, 'preferred_session_minutes'), buffer_minutes: numberValue(form, 'buffer_minutes') })
  if (!parsed.success) return data({ ok: false as const, errors: z.flattenError(parsed.error) }, { status: 400 })
  try { await updatePreferences(parsed.data); return data({ ok: true as const }) }
  catch (error) { return data({ ok: false as const, errors: formErrors(error) }, { status: 400 }) }
}
