import z from "zod";

import { FieldCategoryPipe } from "./field-category-pipe";

describe("FieldCategoryPipe", () => {
  it("create an instance", () => {
    const pipe = new FieldCategoryPipe();
    expect(pipe).toBeTruthy();
  });

  it("maps string types correctly", () => {
    const pipe = new FieldCategoryPipe();
    expect(pipe.transform(z.string())).toBe("optional");
    expect(pipe.transform(z.string().nonempty())).toBe("required");
    expect(pipe.transform(z.string().min(1))).toBe("required");
    expect(pipe.transform(z.string().optional())).toBe("optional");
    expect(pipe.transform(z.string().nullable())).toBe("optional");
    expect(pipe.transform(z.string().nullish())).toBe("optional");
  });

  it("maps array types correctly", () => {
    const pipe = new FieldCategoryPipe();
    expect(pipe.transform(z.string().array())).toBe("optional");
    expect(pipe.transform(z.string().array().nonempty())).toBe("required");
    expect(pipe.transform(z.string().array().min(1))).toBe("required");
    expect(pipe.transform(z.string().array().optional())).toBe("optional");
    expect(pipe.transform(z.string().array().nullable())).toBe("optional");
    expect(pipe.transform(z.string().array().nullish())).toBe("optional");
  });
});
