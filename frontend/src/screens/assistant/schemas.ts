import * as z from "zod";
import type { AssistantInput, AssistantResponse } from "../../types/assistant.ts";

const text = z.string().trim().min(1).max(8000);
const thread_id = z.uuid();
const time_zone = z.string().trim().min(1);

// The `AssistantInput` with the two versions
// first strict object is for user input, second strict object is for command input
export const assistantInputSchema: z.ZodType<AssistantInput> = z.union([
  z.strictObject({ thread_id, time_zone, user_input: text }),

  z.strictObject({
    thread_id, time_zone,
    command: z.union([
      z.strictObject({ action: z.enum(["approve", "cancel"]) }),
      z.strictObject({ action: z.literal("edit"), feedback: text }),
    ]),
  }),

]);

const timestamp = z.iso.datetime({ offset: true });
// The `AssistantResponse` with the three versions

export const assistantResponseSchema: z.ZodType<AssistantResponse> = z.discriminatedUnion("status", [
//   one of the possible responses, completed
  z.object({ status: z.literal("completed"), summary: z.string() }),
//   one of the possible responses, cancelled
  z.object({ status: z.literal("cancelled") }),
//   interruption to check if the drafted schdule fits the user or not (interruptuion)
  z.object({
    status: z.literal("interrupted"),
    interrupts: z.array(z.object({
      type: z.literal("schedule_review"),
      title: z.string(),
      draft: z.object({
        drafts: z.array(z.object({
          task: z.object({
            draft_task_id: z.string().min(1),
            subject: z.number().int().positive(),
            title: z.string(),
            description: z.string(),
            task_type: z.enum(["assignment", "exam", "study", "other"]),
            task_priority: z.enum(["low", "medium", "high"]),
            estimated_minutes: z.number().int().positive(),
            due_date: timestamp,
          }),
          study_sessions: z.array(z.object({
            draft_session_id: z.string().min(1),
            start_at: timestamp,
            end_at: timestamp,
          })).min(1),
        })).min(1),
      }),
    })).min(1),
  }),
]);
