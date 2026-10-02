import { data, type LoaderFunctionArgs } from "react-router";
import { isThreadId } from "./helpers";
import { listThreads } from "./service";

export async function assistantThreadLoader({ params }: LoaderFunctionArgs) {
  const threadId = params.thread_id;
  // checks if the thread_id is valid
  if (!isThreadId(threadId)) {
    throw data(null, { status: 404 });
  }
// gets a list of threads and finds the thread with the matching id, if not found throws a 404 error
  const threads = await listThreads();
  const thread = threads.find((item) => item.id.toLowerCase() === threadId.toLowerCase());
  if (!thread) throw data(null, { status: 404 });

  return { thread };
}
