import z from "zod";

import { FieldCategoryPipe } from "./field-category-pipe";
import { recommended } from "./models/zod-types";

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

    expect(pipe.transform(recommended(z.string()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().nonempty()))).toBe("required");
    expect(pipe.transform(recommended(z.string().min(1)))).toBe("required");
    expect(pipe.transform(recommended(z.string().optional()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().nullable()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().nullish()))).toBe("recommended");
  });

  it("maps array types correctly", () => {
    const pipe = new FieldCategoryPipe();
    expect(pipe.transform(z.string().array())).toBe("optional");
    expect(pipe.transform(z.string().array().nonempty())).toBe("required");
    expect(pipe.transform(z.string().array().min(1))).toBe("required");
    expect(pipe.transform(z.string().array().optional())).toBe("optional");
    expect(pipe.transform(z.string().array().nullable())).toBe("optional");
    expect(pipe.transform(z.string().array().nullish())).toBe("optional");

    expect(pipe.transform(recommended(z.string().array()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().array().nonempty()))).toBe("required");
    expect(pipe.transform(recommended(z.string().array().min(1)))).toBe("required");
    expect(pipe.transform(recommended(z.string().array().optional()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().array().nullable()))).toBe("recommended");
    expect(pipe.transform(recommended(z.string().array().nullish()))).toBe("recommended");
  });
});
