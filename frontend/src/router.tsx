import { createBrowserRouter } from 'react-router'
import { DashboardLayout } from './components/DashboardLayout'
import { RouteErrorPage } from './components/DashboardParts'
import { loginAction, registrationAction } from './screens/auth/actions'
import { LoginPage } from './screens/auth/LoginPage'
import { RegistrationPage } from './screens/auth/RegistrationPage'
import { logoutAction } from './screens/auth/logout'
import { OverviewPage } from './screens/overview/OverviewPage'
import { dashboardLoader, overviewLoader } from './screens/overview/loaders'
import { PreferencesPage } from './screens/preferences/PreferencesPage'
import { preferencesAction } from './screens/preferences/actions'
import { preferencesLoader } from './screens/preferences/loaders'
import { SubjectCreatePage } from './screens/subjects/SubjectCreatePage'
import { SubjectDetailPage } from './screens/subjects/SubjectDetailPage'
import { SubjectEditPage } from './screens/subjects/SubjectEditPage'
import { SubjectsPage } from './screens/subjects/SubjectsPage'
import { createSubjectAction, deleteSubjectAction, editSubjectAction } from './screens/subjects/actions'
import { subjectLoader, subjectsLoader } from './screens/subjects/loaders'
import { TaskCreatePage } from './screens/tasks/TaskCreatePage'
import { TaskDetailPage } from './screens/tasks/TaskDetailPage'
import { TaskEditPage } from './screens/tasks/TaskEditPage'
import { TasksPage } from './screens/tasks/TasksPage'
import { createTaskAction, deleteTaskAction, editTaskAction } from './screens/tasks/actions'
import { taskFormLoader, taskLoader, tasksLoader } from './screens/tasks/loaders'
import { SessionCreatePage } from './screens/study-sessions/SessionCreatePage'
import { SessionDetailPage } from './screens/study-sessions/SessionDetailPage'
import { SessionEditPage } from './screens/study-sessions/SessionEditPage'
import { SessionsPage } from './screens/study-sessions/SessionsPage'
import { createSessionAction, deleteSessionAction, editSessionAction } from './screens/study-sessions/actions'
import { sessionFormLoader, sessionLoader, sessionsLoader } from './screens/study-sessions/loaders'
import { WelcomePage } from './screens/welcome/WelcomePage'

const router = createBrowserRouter([
  { path: '/', Component: WelcomePage },
  { path: '/register', Component: RegistrationPage, action: registrationAction },
  { path: '/login', Component: LoginPage, action: loginAction },
  { path: '/app', Component: DashboardLayout, loader: dashboardLoader, ErrorBoundary: RouteErrorPage, children: [
    { index: true, Component: OverviewPage, loader: overviewLoader },
    { path: 'logout', action: logoutAction },
    { path: 'subjects', Component: SubjectsPage, loader: subjectsLoader },
    { path: 'subjects/new', Component: SubjectCreatePage, action: createSubjectAction },
    { path: 'subjects/:id', Component: SubjectDetailPage, loader: subjectLoader },
    { path: 'subjects/:id/edit', Component: SubjectEditPage, loader: subjectLoader, action: editSubjectAction },
    { path: 'subjects/:id/delete', action: deleteSubjectAction },
    { path: 'tasks', Component: TasksPage, loader: tasksLoader },
    { path: 'tasks/new', Component: TaskCreatePage, loader: taskFormLoader, action: createTaskAction },
    { path: 'tasks/:id', Component: TaskDetailPage, loader: taskLoader },
    { path: 'tasks/:id/edit', Component: TaskEditPage, loader: taskFormLoader, action: editTaskAction },
    { path: 'tasks/:id/delete', action: deleteTaskAction },
    { path: 'study-sessions', Component: SessionsPage, loader: sessionsLoader },
    { path: 'study-sessions/new', Component: SessionCreatePage, loader: sessionFormLoader, action: createSessionAction },
    { path: 'study-sessions/:id', Component: SessionDetailPage, loader: sessionLoader },
    { path: 'study-sessions/:id/edit', Component: SessionEditPage, loader: sessionFormLoader, action: editSessionAction },
    { path: 'study-sessions/:id/delete', action: deleteSessionAction },
    { path: 'preferences', Component: PreferencesPage, loader: preferencesLoader, action: preferencesAction },
  ] },
])
export default router
