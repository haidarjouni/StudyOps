import { createBrowserRouter } from 'react-router'
import { WelcomePage } from './screens/welcome/WelcomePage'

const router = createBrowserRouter([
  {
    path: '/',
    Component: WelcomePage,
  },
])

export default router
