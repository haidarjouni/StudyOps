import { useEffect } from "react";
import { useLoaderData } from "react-router";
import { PageHeading } from "../../components/DashboardParts";
import { SessionForm } from "../../components/SessionForm";
import type { sessionFormLoader } from "./loaders";
export function SessionEditPage() {
  const { subjects, tasks, session } =
    useLoaderData<typeof sessionFormLoader>();
  useEffect(() => {
    document.title = "Edit session | StudyOps";
  }, []);
  return (
    <>
      <PageHeading
        title="Edit session"
        description={session?.subject.name ?? ""}
      />
      <SessionForm session={session} subjects={subjects} tasks={tasks} />
    </>
  );
}
