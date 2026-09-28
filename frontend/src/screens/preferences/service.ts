import { apiRequest } from '../../lib/api'
import type { Preferences } from '../../types/preferences'
export const getPreferences = () => apiRequest<Preferences>('/api/study_preference/me')
export const updatePreferences = (input: Preferences) => apiRequest<Preferences>('/api/study_preference/me', 'PATCH', input)
