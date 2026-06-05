export interface Mitarbeiter {
  id: string;
  vorname: string;
  nachname: string;
  geburtsdatum: Date;
}

export interface Project {
  id: string;
  name: string;
  beschreibung: string;
  startdatum: Date;
  enddatum: Date;
  mitarbeiter: Mitarbeiter[];
}

export interface PaginatedPreviewItems {
  items: Project[];
  total: number;
}
