import type { Mitarbeiter, Project } from "./project.model";

export interface ProjectFormValue {
  name: string;
  beschreibung: string;
  startdatum: Date | null;
  enddatum: Date | null;
  mitarbeiterIds: string[];
}

export function createEmptyProjectFormValue(): ProjectFormValue {
  //Creates a new project form value with the default initial state.
  return {
    name: "",
    beschreibung: "",
    startdatum: null,
    enddatum: null,
    mitarbeiterIds: [],
  };
}

export function projectToFormValue(project: Project): ProjectFormValue {
  // Converts a Project object to a ProjectFormValue object, extracting the relevant fields and mapping the Mitarbeiter array to an array of their IDs.
  return {
    name: project.name,
    beschreibung: project.beschreibung,
    startdatum: project.startdatum,
    enddatum: project.enddatum,
    mitarbeiterIds: project.mitarbeiter.map((employee) => employee.id),
  };
}

export function selectedMitarbeiterFromIds(
/**
 * Resolves a list of employee IDs to corresponding employee objects.
 * Only employees contained in provided list of employees are returned. IDs that cannot be matched are ignored.
 */
  mitarbeiterIds: string[],
  availableMitarbeiter: readonly Mitarbeiter[],
): Mitarbeiter[] {
  const selectedIds = new Set(mitarbeiterIds);
  return availableMitarbeiter.filter((employee) => selectedIds.has(employee.id));
}
