import type { RegistrationField as RegistrationFieldName } from '../types/auth'

interface RegistrationFieldProps {
  name: RegistrationFieldName
  label: string
  type?: 'text' | 'email' | 'password' | 'time' | 'number'
  autoComplete?: string
  defaultValue?: string | number
  min?: number
  max?: number
  maxLength?: number
  hint?: string
  error?: string
}

export function RegistrationField({
  name,
  label,
  type = 'text',
  autoComplete,
  defaultValue,
  min,
  max,
  maxLength,
  hint,
  error,
}: RegistrationFieldProps) {
  const hintId = hint ? `${name}-hint` : undefined
  const errorId = error ? `${name}-error` : undefined

  return (
    <div className="min-w-0">
      <label htmlFor={name} className="mb-2 block text-sm font-bold text-text-strong">
        {label}
      </label>
      <input
        id={name}
        name={name}
        type={type}
        autoComplete={autoComplete}
        defaultValue={defaultValue}
        min={min}
        max={max}
        maxLength={maxLength}
        required
        aria-invalid={error ? true : undefined}
        aria-describedby={[hintId, errorId].filter(Boolean).join(' ') || undefined}
        className="min-h-12 w-full rounded-xl border border-border bg-cream px-4 py-3 text-base text-text-strong outline-none transition-colors duration-200 placeholder:text-text-muted hover:border-primary focus-visible:border-primary-dark focus-visible:ring-3 focus-visible:ring-primary/25 aria-invalid:border-coral-dark aria-invalid:focus-visible:ring-coral/25 motion-reduce:transition-none"
      />
      {hint ? <p id={hintId} className="mt-2 text-xs leading-5 text-text-muted">{hint}</p> : null}
      {error ? <p id={errorId} className="mt-2 text-sm font-medium text-error-dark">{error}</p> : null}
    </div>
  )
}
