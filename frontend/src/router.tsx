import { createBrowserRouter } from "react-router";
import { createThreadAction, deleteThreadAction } from "./screens/assistant/actions";
import { assistantThreadLoader } from "./screens/assistant/loaders";
import { AssistantThreadPage } from "./screens/assistant/AssistantThreadPage";
import { DashboardLayout } from "./components/DashboardLayout";
import { RouteErrorPage } from "./components/DashboardParts";
import { loginAction, registrationAction } from "./screens/auth/actions";
import { LoginPage } from "./screens/auth/LoginPage";
import { RegistrationPage } from "./screens/auth/RegistrationPage";
import { logoutAction } from "./screens/auth/logout";
import { OverviewPage } from "./screens/overview/OverviewPage";
import { dashboardLoader, overviewLoader } from "./screens/overview/loaders";
import { PreferencesPage } from "./screens/preferences/PreferencesPage";
import { preferencesAction } from "./screens/preferences/actions";
import { preferencesLoader } from "./screens/preferences/loaders";
import { SubjectCreatePage } from "./screens/subjects/SubjectCreatePage";
import { SubjectDetailPage } from "./screens/subjects/SubjectDetailPage";
import { SubjectEditPage } from "./screens/subjects/SubjectEditPage";
import { SubjectsPage } from "./screens/subjects/SubjectsPage";
import {
  createSubjectAction,
  deleteSubjectAction,
  editSubjectAction,
} from "./screens/subjects/actions";
import { subjectLoader, subjectsLoader } from "./screens/subjects/loaders";
import { TaskCreatePage } from "./screens/tasks/TaskCreatePage";
import { TaskDetailPage } from "./screens/tasks/TaskDetailPage";
import { TaskEditPage } from "./screens/tasks/TaskEditPage";
import { TasksPage } from "./screens/tasks/TasksPage";
import {
  createTaskAction,
  deleteTaskAction,
  editTaskAction,
} from "./screens/tasks/actions";
import {
  taskFormLoader,
  taskLoader,
  tasksLoader,
} from "./screens/tasks/loaders";
import { SessionCreatePage } from "./screens/study-sessions/SessionCreatePage";
import { SessionDetailPage } from "./screens/study-sessions/SessionDetailPage";
import { SessionEditPage } from "./screens/study-sessions/SessionEditPage";
import { SessionsPage } from "./screens/study-sessions/SessionsPage";
import {
  createSessionAction,
  deleteSessionAction,
  editSessionAction,
} from "./screens/study-sessions/actions";
import {
  sessionFormLoader,
  sessionLoader,
  sessionsLoader,
} from "./screens/study-sessions/loaders";
import { WelcomePage } from "./screens/welcome/WelcomePage";

const router = createBrowserRouter([
  { path: "/", Component: WelcomePage },
  {
    path: "/register",
    Component: RegistrationPage,
    action: registrationAction,
  },
  { path: "/login", Component: LoginPage, action: loginAction },
  {
    path: "/app",
    Component: DashboardLayout,
    loader: dashboardLoader,
    ErrorBoundary: RouteErrorPage,
    children: [
      { index: true, Component: OverviewPage, loader: overviewLoader },
      { path: "logout", action: logoutAction },
      {
        path: "assistant",
        children: [
          { path: "new", action: createThreadAction },
          {
            path: ":thread_id",
            Component: AssistantThreadPage,
            loader: assistantThreadLoader,
            action: deleteThreadAction,
          },
        ],
      },
      {
        path: "subjects",
        children: [
          { index: true, Component: SubjectsPage, loader: subjectsLoader },
          {
            path: "new",
            Component: SubjectCreatePage,
            action: createSubjectAction,
          },
          { path: ":id", Component: SubjectDetailPage, loader: subjectLoader },
          {
            path: ":id/edit",
            Component: SubjectEditPage,
            loader: subjectLoader,
            action: editSubjectAction,
          },
          { path: ":id/delete", action: deleteSubjectAction },
        ],
      },
      {
        path: "tasks",
        children: [
          { index: true, Component: TasksPage, loader: tasksLoader },
          {
            path: "new",
            Component: TaskCreatePage,
            loader: taskFormLoader,
            action: createTaskAction,
          },
          { path: ":id", Component: TaskDetailPage, loader: taskLoader },
          {
            path: ":id/edit",
            Component: TaskEditPage,
            loader: taskFormLoader,
            action: editTaskAction,
          },
          { path: ":id/delete", action: deleteTaskAction },
        ],
      },
      {
        path: "study-sessions",
        children: [
          { index: true, Component: SessionsPage, loader: sessionsLoader },
          {
            path: "new",
            Component: SessionCreatePage,
            loader: sessionFormLoader,
            action: createSessionAction,
          },
          { path: ":id", Component: SessionDetailPage, loader: sessionLoader },
          {
            path: ":id/edit",
            Component: SessionEditPage,
            loader: sessionFormLoader,
            action: editSessionAction,
          },
          { path: ":id/delete", action: deleteSessionAction },
        ],
      },
      {
        path: "preferences",
        Component: PreferencesPage,
        loader: preferencesLoader,
        action: preferencesAction,
      },
    ],
  },
]);
export default router;
