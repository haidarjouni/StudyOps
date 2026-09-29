import { apiRequest } from "../../lib/api";
import type { StudySession, SessionInput } from "../../types/sessions";
// empty search by default, if search is provided, it will be appended to the url
export const listSessions = (search = "")  =>
    // send a get request to the api with the search params
  apiRequest<StudySession[]>(`/api/study_session/${search}`);
export const getSession = (id: string) =>
  apiRequest<StudySession>(`/api/study_session/${id}/`);
export const createSession = (input: SessionInput) =>
  apiRequest<StudySession>("/api/study_session/", "POST", input);
export const updateSession = (id: string, input: Partial<SessionInput>) =>
  apiRequest<StudySession>(`/api/study_session/${id}/`, "PATCH", input);
export const deleteSession = (id: string) =>
  apiRequest<void>(`/api/study_session/${id}/`, "DELETE");
