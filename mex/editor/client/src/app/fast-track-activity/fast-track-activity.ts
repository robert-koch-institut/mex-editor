import { Component, signal } from "@angular/core";
import { form, minLength, required, FormField, FormRoot } from "@angular/forms/signals";
import { MatInput } from "@angular/material/input";
import { MatFormField, MatLabel, MatError } from "@angular/material/select";

interface CreateContactPointModel {
  $type: "CreateContactPointModel";
  email: string;
}
interface CreatePersonModel {
  $type: "CreatePersonModel";
  firstName: number;
  lastName: number;
}
type CreateContactModel = CreateContactPointModel | CreatePersonModel;
interface FastTrackActivityModel {
  title: string;
  contact: (string | CreateContactModel)[];
}

@Component({
  selector: "mex-fast-track-activity",
  imports: [FormField, MatFormField, MatLabel, MatError, MatInput, MatError, FormRoot],
  templateUrl: "./fast-track-activity.html",
  styleUrl: "./fast-track-activity.scss",
})
export class FastTrackActivity {
  model = signal<FastTrackActivityModel>({
    title: "",
    contact: [""],
  });

  activityForm = form(this.model, (schema) => {
    required(schema.title, { message: "Title is required" });
    minLength(schema.title, 3, { message: "Title must be at least 3 characters long" });
  });

  onSubmit($event: SubmitEvent) {
    // eslint-disable-next-line no-console
    console.log("Submitted", $event, this.model());
  }
}
