import { createBrowserRouter } from 'react-router'
import { registrationAction } from './screens/auth/actions'
import { RegistrationPage } from './screens/auth/RegistrationPage'
import { WelcomePage } from './screens/welcome/WelcomePage'

const router = createBrowserRouter([
  {
    path: '/',
    Component: WelcomePage,
  },
  {
    path: '/register',
    Component: RegistrationPage,
    action: registrationAction,
  },
])

export default router
