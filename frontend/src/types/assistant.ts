export type Thread = {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
};

export type AssistantCommand =
  | { action: "approve" | "cancel" }
  | { action: "edit"; feedback: string };

export type AssistantInput = { thread_id: string; time_zone: string } & (
  | { user_input: string; command?: never }
  | { command: AssistantCommand; user_input?: never }
);

export type ScheduleReview = {
  type: "schedule_review";
  title: string;
  draft: {
    drafts: {
      task: {
        draft_task_id: string;
        subject: number;
        title: string;
        description: string;
        task_type: "assignment" | "exam" | "study" | "other";
        task_priority: "low" | "medium" | "high";
        estimated_minutes: number;
        due_date: string;
      };
      study_sessions: {
        draft_session_id: string;
        start_at: string;
        end_at: string;
      }[];
    }[];
  };
};

export type AssistantResponse =
  | { status: "interrupted"; interrupts: ScheduleReview[] }
  | { status: "completed"; summary: string }
  | { status: "cancelled" };

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  kind: "chat" | "command" | "completed" | "cancelled";
};
