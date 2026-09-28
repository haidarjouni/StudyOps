import type { Subject } from "./subjects";
import type { Task } from "./tasks";
export type SessionStatus = "scheduled" | "completed" | "cancelled";
export type StudySession = {
  id: number;
  user: number;
  subject: Subject;
  task: Task | null;
  start_at: string;
  end_at: string;
  status: SessionStatus;
  created_at: string;
  updated_at: string;
};
export type SessionInput = {
  subject_id: number;
  task_id: number | null;
  start_at: string;
  end_at: string;
  status: SessionStatus;
};
