export interface Text {
  value: string;
  language?: string | null;
}

export interface PreviewOrganizationalUnit {
  identifier: string;
  name: Text[];
}

export interface UnitOption {
  id: string;
  label: string;
}
