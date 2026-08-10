import { Service } from "@angular/core";

/**
 * Model for found contacts.
 */
export interface SearchContact {
  $type: "person" | "mail";
  id: string;
  label: string;
}

@Service()
/**
 * A service to search for contacts.
 */
export class ContactSearch {
  private readonly data: SearchContact[] = [
    { id: "1LhqzR0vmWAfFl52h1U06", $type: "person", label: "Anna Müller" },
    // { id: "p2", $type: "person", label: "Bernd Koch" },
    // { id: "m1", $type: "mail", label: "Robert Koch Institut" },
    // { id: "m2", $type: "mail", label: "Charité Berlin" },
    // …
  ];

  search(query: string, filter: { persons: boolean; mail: boolean }): SearchContact[] {
    const q = query.toLowerCase();
    const matches = (e: SearchContact) => e.label.toLowerCase().includes(q);

    let result: SearchContact[] = [];

    if (filter.persons) {
      result = [...this.data.filter((e) => e.$type === "person" && matches(e))];
    }
    if (filter.mail) {
      result = [...result, ...this.data.filter((e) => e.$type === "mail" && matches(e))];
    }

    return result;
  }
}
