import type { LoaderFunctionArgs } from "react-router";
import { listSubjects } from "../subjects/service";
import { getTask, listTasks } from "./service";
const filterKeys = ["subject", "task_type", "task_status", "task_priority"];
export async function tasksLoader({ request }: LoaderFunctionArgs) {
  const source = new URL(request.url).searchParams;
  const filters = new URLSearchParams();
  filterKeys.forEach((key) => {
    if (source.get(key)) filters.set(key, source.get(key)!);
  });
  const [tasks, subjects] = await Promise.all([
    listTasks(filters.size ? `?${filters}` : ""),
    listSubjects(),
  ]);
  return { tasks, subjects };
}
export async function taskFormLoader({ params }: LoaderFunctionArgs) {
  const [subjects, task] = await Promise.all([
    listSubjects(),
    params.id ? getTask(params.id) : Promise.resolve(null),
  ]);
  return { subjects, task };
}
export async function taskLoader({ params }: LoaderFunctionArgs) {
  const [task, subjects] = await Promise.all([
    getTask(params.id!),
    listSubjects(),
  ]);
  return { task, subjects };
}
