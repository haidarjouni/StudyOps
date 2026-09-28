import type { LoaderFunctionArgs } from "react-router";
import { getSubject, listSubjects } from "./service";
export async function subjectsLoader() {
    // get the subjects object from the loader data using useLoaderData
  return { subjects: await listSubjects() };
}
export async function subjectLoader({ params }: LoaderFunctionArgs) {
    // get the subject object from the loader data using useLoaderData
  return { subject: await getSubject(params.id!) };
}
