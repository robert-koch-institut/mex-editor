import { TypeToIconNamePipe } from "./type-to-icon-name-pipe";

describe("TypeToIconNamePipe", () => {
  let pipe: TypeToIconNamePipe;

  beforeEach(() => {
    pipe = new TypeToIconNamePipe();
  });

  it("maps a known type to its icon name", () => {
    expect(pipe.transform("Person")).toBe("person");
    expect(pipe.transform("ContactPoint")).toBe("mail");
    expect(pipe.transform("OrganizationalUnit")).toBe("ad_group");
  });

  it("strips Merged/Extracted/Preview/Create prefixes before mapping", () => {
    expect(pipe.transform("MergedPerson")).toBe("person");
    expect(pipe.transform("ExtractedContactPoint")).toBe("mail");
    expect(pipe.transform("PreviewOrganizationalUnit")).toBe("ad_group");
    expect(pipe.transform("CreatePerson")).toBe("person");
  });

  it("falls back to 'question_mark' for an unknown type", () => {
    expect(pipe.transform("SomethingUnknown")).toBe("question_mark");
  });

  it("uses a custom fallback when given one", () => {
    expect(pipe.transform("SomethingUnknown", { fallback: "help" })).toBe("help");
  });

  it("applies prefix/suffix around a mapped icon name", () => {
    expect(pipe.transform("Person", { prefix: "icon-", suffix: "-24" })).toBe("icon-person-24");
  });
});
