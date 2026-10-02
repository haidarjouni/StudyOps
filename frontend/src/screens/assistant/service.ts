import { apiRequest } from "../../lib/api";
import type { Thread } from "../../types/assistant";

export const listThreads = () => apiRequest<Thread[]>("/api/thread/");

export const createThread = () =>
  apiRequest<Thread>("/api/thread/", "POST", {});

export const deleteThread = (id: string) =>
  apiRequest<void>(`/api/thread/${encodeURIComponent(id)}/`, "DELETE");
