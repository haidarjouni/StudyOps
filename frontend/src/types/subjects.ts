export type Subject = {
  id: number;
  user: number;
  name: string;
  code: string;
  semester: number;
  created_at: string;
  updated_at: string;
};
export type SubjectInput = Pick<Subject, "name" | "code" | "semester">;
