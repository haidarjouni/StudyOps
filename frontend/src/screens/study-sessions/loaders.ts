import type { LoaderFunctionArgs } from "react-router";
import { listSubjects } from "../subjects/service";
import { listTasks } from "../tasks/service";
import { getSession, listSessions } from "./service";
export async function sessionsLoader({ request }: LoaderFunctionArgs) {
  const source = new URL(request.url).searchParams;
  const filters = new URLSearchParams();
//   loop through every key 
  for (const key of ["subject", "task", "status"])
    // get the one that is not null
    if (source.get(key))
        // set the filter to the value of the key
        filters.set(key, source.get(key)!);
    // run a paralel get requests to get the filtered sessions, subjects and tasks
  const [sessions, subjects, tasks] = await Promise.all([
    // if any filter are set 
    listSessions(filters.size ? `?${filters}` : ""),
    listSubjects(),
    listTasks(),
  ]);
  return { sessions, subjects, tasks };
}

export async function sessionFormLoader({ params }: LoaderFunctionArgs) {
  const [subjects, tasks, session] = await Promise.all([
    listSubjects(),
    listTasks(),
    params.id ? getSession(params.id) : Promise.resolve(null),
  ]);
  return { subjects, tasks, session };
}
export async function sessionLoader({ params }: LoaderFunctionArgs) {
  return { session: await getSession(params.id!) };
}
