import { ToLabelPipe } from "./to-label-pipe";

// eslint-disable-next-line max-lines-per-function
describe("ToLabelPipe", () => {
  let pipe: ToLabelPipe;

  beforeEach(() => {
    pipe = new ToLabelPipe();
  });

  it("create an instance", () => {
    expect(pipe).toBeTruthy();
  });

  describe("Concept", () => {
    it("uses prefLabel in the requested language", () => {
      const concept = {
        identifier: "concept-1",
        prefLabel: { de: "Bevölkerung", en: "Population" },
        altLabel: [],
        inScheme: "scheme-1",
      };
      expect(pipe.transform(concept, "de")).toBe("Bevölkerung");
      expect(pipe.transform(concept, "en")).toBe("Population");
    });

    it("falls back to an altLabel in the requested language when prefLabel is missing it", () => {
      const concept = {
        identifier: "concept-1",
        prefLabel: { de: "Bevölkerung" },
        altLabel: [{ de: "Bevölkerungszahl", en: "Population count" }],
        inScheme: "scheme-1",
      };
      expect(pipe.transform(concept, "en")).toBe("Population count");
    });

    it("falls back to the identifier when neither prefLabel nor altLabel has the language", () => {
      const concept = {
        identifier: "concept-1",
        prefLabel: {},
        altLabel: [],
        inScheme: "scheme-1",
      };
      expect(pipe.transform(concept, "en")).toBe("concept-1");
    });
  });

  describe("PreviewOrganizationalUnit", () => {
    it("prefers shortName", () => {
      const unit = {
        $type: "PreviewOrganizationalUnit" as const,
        identifier: "unit-1",
        shortName: [{ value: "RKI" }],
        name: [{ value: "Robert Koch Institut" }],
        alternativeName: [],
      };
      expect(pipe.transform(unit, "de")).toBe("RKI");
    });

    it("falls back to name when shortName is empty", () => {
      const unit = {
        $type: "PreviewOrganizationalUnit" as const,
        identifier: "unit-1",
        shortName: [],
        name: [{ value: "Robert Koch Institut" }],
        alternativeName: [],
      };
      expect(pipe.transform(unit, "de")).toBe("Robert Koch Institut");
    });

    it("falls back to alternativeName when shortName and name are both empty", () => {
      const unit = {
        $type: "PreviewOrganizationalUnit" as const,
        identifier: "unit-1",
        shortName: [],
        name: [],
        alternativeName: [{ value: "RKI Alt" }],
      };
      expect(pipe.transform(unit, "de")).toBe("RKI Alt");
    });

    it("picks the language-matching entry out of a Text[]-shaped field", () => {
      const unit = {
        $type: "PreviewOrganizationalUnit" as const,
        identifier: "unit-1",
        shortName: [
          { language: "de" as const, value: "RKI" },
          { language: "en" as const, value: "RKI (EN)" },
        ],
        name: [],
        alternativeName: [],
      };
      expect(pipe.transform(unit, "en")).toBe("RKI (EN)");
    });

    it("falls back to an unlabeled Text entry when none matches the language", () => {
      const unit = {
        $type: "PreviewOrganizationalUnit" as const,
        identifier: "unit-1",
        shortName: [{ value: "RKI (no language)" }],
        name: [],
        alternativeName: [],
      };
      expect(pipe.transform(unit, "en")).toBe("RKI (no language)");
    });
  });

  describe("PreviewPerson", () => {
    it("uses fullName", () => {
      const person = {
        $type: "PreviewPerson" as const,
        identifier: "person-1",
        fullName: ["Jane Doe"],
      };
      expect(pipe.transform(person, "de")).toBe("Jane Doe");
    });
  });

  describe("PreviewContactPoint", () => {
    it("uses email", () => {
      const contactPoint = {
        $type: "PreviewContactPoint" as const,
        identifier: "contact-1",
        email: ["jane.doe@example.org"],
      };
      expect(pipe.transform(contactPoint, "de")).toBe("jane.doe@example.org");
    });
  });

  describe("CreatePerson / CreateContactPoint (unsaved draft items)", () => {
    it("prefixes a CreatePerson's label with a star", () => {
      const item = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
      expect(pipe.transform(item, "de")).toBe("⋆ Jane Doe");
    });

    it("prefixes a CreateContactPoint's label with a star", () => {
      const item = { $type: "CreateContactPoint" as const, email: "jane.doe@example.org" };
      expect(pipe.transform(item, "de")).toBe("⋆ jane.doe@example.org");
    });
  });

  it("return the type and identifier when no label can be derived from any field", () => {
    const unit = {
      $type: "PreviewOrganizationalUnit" as const,
      identifier: "unit-1",
      shortName: [],
      name: [],
      alternativeName: [],
    };
    expect(pipe.transform(unit, "de")).toBe("OrganizationalUnit | unit-1");
  });
});
