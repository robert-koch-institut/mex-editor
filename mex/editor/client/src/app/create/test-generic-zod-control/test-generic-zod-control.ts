import { Component, signal } from "@angular/core";
import { form, FormRoot, validateStandardSchema } from "@angular/forms/signals";
import z from "zod";

import type { FastTrackActivityModel } from "../../fast-track/fast-track-activity.model";
import { FastTrackActivityModelSchema } from "../../fast-track/fast-track-activity.model";
import { addFieldLabelKeysAndDescriptionKeys } from "../../shared/field-metadata.pipe";
import { TextSchema } from "../../shared/models/generated/shared";
import { ZodFieldEditor } from "../../shared/zod-field-editor/zod-field-editor";

// eslint-disable-next-line @typescript-eslint/naming-convention
const SimpleSchema = z.object({
  title: TextSchema.nullable(),
  titleMandatory: TextSchema.nonoptional(),
  titleArray: TextSchema.array(),
  titleArrayMandatory: TextSchema.array().min(2),

  name: z.string().optional(),
  nameMandatory: z.string().nonempty(),
  nameArray: z.string().array(),
  nameArrayMandatory: TextSchema.array().min(2),

  other: z.object({
    otherProp: z.string().min(1),
    otherMandatoryProp: z.string().nonoptional(),
    otherArrayProp: z.string().min(1).array(),
    otherMandatoryArrayProp: z.string().array().min(2),
    otherMandatoryArrayWithInnerProp: z.string().min(1).array().min(2),
  }),
});

type Simple = z.infer<typeof SimpleSchema>;

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
  simpleModel = signal<Simple>({
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
      otherMandatoryProp: "",
      otherArrayProp: [],
      otherMandatoryArrayProp: [],
      otherMandatoryArrayWithInnerProp: [],
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
        action: async (field) => {
          console.log("submit simple", field().value());
        },
        onInvalid: (field) => {
          const firstError = field().errorSummary()[0];
          firstError?.fieldTree().focusBoundControl();
        },
        ignoreValidators: "all",
      },
    },
  );

  fastActivityModel = signal<FastTrackActivityModel>({
    $type: "FastTrackActivityModel",
    title: "",
    abstract: "",
    contact: [],
    responsibleUnit: [],
    activityType: [],
    shortName: "",
    involvedPerson: [],
    involvedUnit: [],
    start: null,
    end: null,
    funderOrCommissioner: [],
    website: [],
  });
  fastActivitySchema = FastTrackActivityModelSchema;
  fastActivityForm = form(
    this.fastActivityModel,
    (schema) => {
      validateStandardSchema(schema, FastTrackActivityModelSchema);
      addFieldLabelKeysAndDescriptionKeys(schema, FastTrackActivityModelSchema, "Activity");
    },
    {
      submission: {
        action: async (field) => {
          console.log("submit fast activity", field());
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
