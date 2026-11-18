import { Component, signal } from "@angular/core";
import { form, FormRoot, validateStandardSchema } from "@angular/forms/signals";
import z from "zod";

import { TextSchema } from "../../shared/models/generated/shared";
import { ZodFieldEditor } from "../zod-field-editor/zod-field-editor";

// eslint-disable-next-line @typescript-eslint/naming-convention
const SimpleSchema = z.object({
  title: TextSchema.nullable(),
  titleMandatory: TextSchema.nonoptional(),
  titleArray: TextSchema.array(),
  titleArrayMandatory: TextSchema.array().min(1),

  name: z.string().optional(),
  nameMandatory: z.string().nonempty(),
  nameArray: z.string().array(),
  nameArrayMandatory: TextSchema.array().min(1),

  other: z.object({
    otherProp: z.string(),
  }),
});

type SimpleSchema = z.infer<typeof SimpleSchema>;

@Component({
  imports: [FormRoot, ZodFieldEditor],
  selector: "mex-test-generic-zod-control",
  styleUrl: "./test-generic-zod-control.scss",
  templateUrl: "./test-generic-zod-control.html",
})
/**
 * Test
 */
export class TestGenericZodControl {
  simpleModel = signal<SimpleSchema>({
    title: null,
    titleMandatory: { value: "", language: null },
    titleArray: [],
    titleArrayMandatory: [],
    name: "",
    nameMandatory: "",
    nameArray: [],
    nameArrayMandatory: [],
    other: {
      otherProp: "",
    },
  });
  simpleSchema = SimpleSchema;
  simpleForm = form(
    this.simpleModel,
    (schema) => {
      validateStandardSchema(schema, SimpleSchema);
    },
    {
      submission: {
        action: async (_field) => {
          console.log("submit", this.simpleModel());
        },
        onInvalid: (field) => {
          const firstError = field().errorSummary()[0];
          firstError?.fieldTree().focusBoundControl();
        },
        ignoreValidators: "all",
      },
    },
  );
}
