import { getPreferences } from "./service";
export async function preferencesLoader() {
  return { preferences: await getPreferences() };
}
