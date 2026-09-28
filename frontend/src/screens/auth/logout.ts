import { redirect } from 'react-router'
import { apiRequest } from '../../lib/api'
export async function logoutAction() {
  await apiRequest<{ message: string }>('/api/accounts/logout/', 'POST')
  return redirect('/login?logged_out=1')
}
