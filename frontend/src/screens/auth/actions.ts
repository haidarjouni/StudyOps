import { data, type ActionFunctionArgs } from 'react-router'
import * as z from 'zod'
import type {
  RegistrationErrors,
  RegistrationField,
  RegistrationInput,
} from '../../types/auth'

interface RegistrationFormValues {
  username: string
  email: string
  password: string
  confirm_password: string
  timezone: string
  earliest_study_time: string
  latest_study_time: string
  preferred_session_minutes: number
  buffer_minutes: number
}

const timeSchema = z.string().regex(/^([01]\d|2[0-3]):[0-5]\d$/, 'Enter a valid time.')

const registrationSchema: z.ZodType<RegistrationFormValues> = z
  .strictObject({
    username: z.string().trim().min(1, 'Enter a username.').max(150, 'Use 150 characters or fewer.'),
    email: z.email('Enter a valid email address.'),
    password: z.string().min(1, 'Enter a password.'),
    confirm_password: z.string().min(1, 'Confirm your password.'),
    timezone: z.string().min(1, 'Enter a time zone.').max(64, 'Use 64 characters or fewer.').refine((value) => {
      try {
        new Intl.DateTimeFormat('en', { timeZone: value })
        return true
      } catch {
        return false
      }
    }, 'Enter a valid IANA time zone.'),
    earliest_study_time: timeSchema,
    latest_study_time: timeSchema,
    preferred_session_minutes: z.number().int().positive('Enter a number greater than zero.'),
    buffer_minutes: z.number().int().nonnegative('Enter zero or a positive number.'),
  })
  .refine((values) => values.earliest_study_time < values.latest_study_time, {
    path: ['latest_study_time'],
    message: 'End time must be after start time.',
  })
  .refine((values) => values.password === values.confirm_password, {
    path: ['confirm_password'],
    message: 'Passwords do not match.',
  })

function stringValue(formData: FormData, name: string): string {
  const value = formData.get(name)
  return typeof value === 'string' ? value.trim() : ''
}

function numberValue(formData: FormData, name: string): number {
  const value = stringValue(formData, name)
  return value === '' ? Number.NaN : Number(value)
}

function formCandidate(formData: FormData): RegistrationFormValues {
  const password = formData.get('password')
  const confirmation = formData.get('confirm_password')

  return {
    username: stringValue(formData, 'username'),
    email: stringValue(formData, 'email'),
    password: typeof password === 'string' ? password : '',
    confirm_password: typeof confirmation === 'string' ? confirmation : '',
    timezone: stringValue(formData, 'timezone'),
    earliest_study_time: stringValue(formData, 'earliest_study_time'),
    latest_study_time: stringValue(formData, 'latest_study_time'),
    preferred_session_minutes: numberValue(formData, 'preferred_session_minutes'),
    buffer_minutes: numberValue(formData, 'buffer_minutes'),
  }
}

function toRegistrationInput(values: RegistrationFormValues): RegistrationInput {
  return {
    username: values.username,
    email: values.email,
    password: values.password,
    study_preferences: {
      timezone: values.timezone,
      earliest_study_time: `${values.earliest_study_time}:00`,
      latest_study_time: `${values.latest_study_time}:00`,
      preferred_session_minutes: values.preferred_session_minutes,
      buffer_minutes: values.buffer_minutes,
    },
  }
}

function errorMessages(value: unknown): string[] {
  if (typeof value === 'string') return [value]
  if (Array.isArray(value)) return value.flatMap(errorMessages)
  return []
}

function backendErrors(body: unknown): RegistrationErrors {
  const errors: RegistrationErrors = { formErrors: [], fieldErrors: {} }
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    errors.formErrors.push('Please check your details and try again.')
    return errors
  }

  for (const [field, value] of Object.entries(body)) {
    if (field === 'study_preferences' && value && typeof value === 'object' && !Array.isArray(value)) {
      for (const [preference, messages] of Object.entries(value)) {
        if (preference === 'non_field_errors') {
          errors.formErrors.push(...errorMessages(messages))
        } else if (preference in preferenceFields) {
          errors.fieldErrors[preference as RegistrationField] = errorMessages(messages)
        }
      }
    } else if (field in accountFields) {
      errors.fieldErrors[field as RegistrationField] = errorMessages(value)
    } else {
      errors.formErrors.push(...errorMessages(value))
    }
  }

  if (!errors.formErrors.length && !Object.keys(errors.fieldErrors).length) {
    errors.formErrors.push('Please check your details and try again.')
  }
  return errors
}

const accountFields = { username: true, email: true, password: true }
const preferenceFields = {
  timezone: true,
  earliest_study_time: true,
  latest_study_time: true,
  preferred_session_minutes: true,
  buffer_minutes: true,
}

function failure(errors: RegistrationErrors, status: number) {
  return data({ ok: false as const, errors }, { status })
}

export async function registrationAction({ request }: ActionFunctionArgs) {
  const candidate = formCandidate(await request.formData())
  const parsed = registrationSchema.safeParse(candidate)
  if (!parsed.success) {
    const flattened = z.flattenError(parsed.error)
    return failure(flattened, 400)
  }

  const configuredBase = import.meta.env.VITE_API_BASE_URL
  if (!configuredBase) {
    return failure({ formErrors: ['Registration is not configured yet. Please try again later.'], fieldErrors: {} }, 503)
  }

  // The Vite dev proxy forwards this same-origin path to VITE_API_BASE_URL.
  const apiBase = import.meta.env.DEV ? window.location.origin : configuredBase
  const url = new URL('/api/accounts/signup/', apiBase)

  try {
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(toRegistrationInput(parsed.data)),
    })

    if (response.status === 201) return data({ ok: true as const })
    if (response.status === 400) {
      const body: unknown = await response.json().catch(() => null)
      return failure(backendErrors(body), 400)
    }

    return failure({ formErrors: ['Registration could not be completed. Please try again.'], fieldErrors: {} }, response.status)
  } catch {
    return failure({ formErrors: ['Unable to reach StudyOps. Check your connection and try again.'], fieldErrors: {} }, 503)
  }
}
