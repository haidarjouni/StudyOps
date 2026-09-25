export interface StudyPreferencesInput {
  timezone: string
  earliest_study_time: string
  latest_study_time: string
  preferred_session_minutes: number
  buffer_minutes: number
}

export interface RegistrationInput {
  username: string
  email: string
  password: string
  study_preferences: StudyPreferencesInput
}

export type RegistrationField =
  | 'username'
  | 'email'
  | 'password'
  | 'confirm_password'
  | keyof StudyPreferencesInput

export interface RegistrationErrors {
  formErrors: string[]
  fieldErrors: Partial<Record<RegistrationField, string[]>>
}
