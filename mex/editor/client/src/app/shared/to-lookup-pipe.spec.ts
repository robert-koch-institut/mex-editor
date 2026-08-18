import { ToLookupPipe } from "./to-lookup-pipe";

describe("ToLookupPipe", () => {
  let pipe: ToLookupPipe;

  beforeEach(() => {
    pipe = new ToLookupPipe();
  });

  it("create an instance", () => {
    expect(pipe).toBeTruthy();
  });

  it("uses the identifier as id for an existing (saved) item", () => {
    const person = {
      $type: "PreviewPerson" as const,
      identifier: "person-1",
      fullName: ["Jane Doe"],
    };
    const result = pipe.transform(person, "de");

    expect(result.id).toBe("person-1");
    expect(result.label).toBe("Jane Doe");
    expect(result.data).toBe(person);
  });

  it("generates a random id for an unsaved CreateItem entry (it has no identifier yet)", () => {
    const draft = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
    const result = pipe.transform(draft, "de");

    expect(result.id).toBeTruthy();
    expect(result.label).toBe("⋆ Jane Doe");
    expect(result.data).toBe(draft);
  });

  it("generates a different id on each call for CreateItem entries", () => {
    const draft = { $type: "CreateContactPoint" as const, email: "jane.doe@example.org" };
    const first = pipe.transform(draft, "de");
    const second = pipe.transform(draft, "de");

    expect(first.id).not.toBe(second.id);
  });

  it("delegates label generation to ToLabelPipe (language-aware)", () => {
    const concept = {
      identifier: "concept-1",
      prefLabel: { de: "Bevölkerung", en: "Population" },
      altLabel: [],
      inScheme: "scheme-1",
    };
    expect(pipe.transform(concept, "de").label).toBe("Bevölkerung");
    expect(pipe.transform(concept, "en").label).toBe("Population");
  });
});
