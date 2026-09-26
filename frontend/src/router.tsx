import { createBrowserRouter } from 'react-router'
import { loginAction, registrationAction } from './screens/auth/actions'
import { LoginPage } from './screens/auth/LoginPage'
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
  {
    path: '/login',
    Component: LoginPage,
    action: loginAction,
  },
])

export default router
