import { Injectable } from "@angular/core";
import type { Mitarbeiter, Project } from "../models/project.model";

@Injectable({
  providedIn: "root",
})
export class DummyDataService {
  private dummyMitarbeiter: Mitarbeiter[] = [
    {
      id: "m1",
      vorname: "Bernd,",
      nachname: "Das Brot",
      geburtsdatum: new Date("1970-05-15"),
    },
    {
      id: "m2",
      vorname: "Malenia,",
      nachname: "Blade of Miquella",
      geburtsdatum: new Date("1988-03-22"),
    },
  ];

  private dummyProjects: Project[] = [
    {
      id: "p1",
      name: "MEx Editor",
      beschreibung: "",
      startdatum: new Date("2024-01-15"),
      enddatum: new Date("2029-12-31"),
      mitarbeiter: this.dummyMitarbeiter,
    },
  ];

  getProjects(): Project[] {
    return this.dummyProjects;
  }

  getProjectById(id: string): Project | undefined {
    return this.dummyProjects.find((p) => p.id === id);
  }

  getMitarbeiterById(mitarbeiterId: string): Mitarbeiter | undefined {
    return this.dummyMitarbeiter.find((m) => m.id === mitarbeiterId);
  }

  getAvailableMitarbeiter(): Mitarbeiter[] {
    return this.dummyMitarbeiter;
  }

  addProject(project: Project): void {
    this.dummyProjects.push(project);
  }

  updateProject(updatedProject: Project): void {
    const index = this.dummyProjects.findIndex((p) => p.id === updatedProject.id);
    if (index !== -1) {
      this.dummyProjects[index] = updatedProject;
    }
  }
}
