import { Component, signal } from "@angular/core";
import { form, FormField, FormRoot, minLength, required } from "@angular/forms/signals";
import { MatFormField, MatLabel, MatError, MatInput } from "@angular/material/input";
interface FastTrackResourceModel {
  title: string;
}
@Component({
  selector: "mex-fast-track-resource",
  imports: [FormField, MatFormField, MatLabel, MatError, MatInput, MatError, FormRoot],
  templateUrl: "./fast-track-resource.html",
  styleUrl: "./fast-track-resource.scss",
})
export class FastTrackResource {
    model = signal<FastTrackResourceModel>({
    title: "",
  });

  resourceForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
  });

  onSubmit($event: SubmitEvent) {
    // eslint-disable-next-line no-console
    console.log("Submitted", $event, this.model());
  }
}
