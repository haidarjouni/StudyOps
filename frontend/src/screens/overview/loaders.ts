import { redirect, type LoaderFunctionArgs } from "react-router";
import { ApiError, apiRequest } from "../../lib/api";
import type { Subject } from "../../types/subjects";
import type { Task } from "../../types/tasks";
import type { StudySession } from "../../types/sessions";

export async function dashboardLoader() {
  try {
    return {
      user: await apiRequest<{ id: number; username: string }>(
        "/auth/users/me/"
      ),
    };
  } catch (error) {
    if (error instanceof ApiError && error.status === 401)
      throw redirect("/login");
    throw error;
  }
}

export async function overviewLoader({ request }: LoaderFunctionArgs) {
//   get the current time in ISO format
  const now = new Date().toISOString();
//   deconstruct the signal from the request object also ran asyncronously the apiRequest for subjects, tasks and sessions in parallel using Promise.all
  const [subjects, tasks, sessions] = await Promise.all([
    apiRequest<Subject[]>("/api/subject/"),
    apiRequest<Task[]>("/api/study_task/"),
    apiRequest<StudySession[]>(
      `/api/study_session/?start_at__gte=${encodeURIComponent(now)}`
    ),
  ]);
  if (request.signal.aborted)
    return { subjects: [], tasks: [], sessions: [], now };
  return { subjects, tasks, sessions, now };
}
