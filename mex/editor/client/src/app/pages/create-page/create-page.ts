import { Component, input } from "@angular/core";

@Component({
  selector: "app-create-page",
  imports: [],
  templateUrl: "./create-page.html",
  styleUrl: "./create-page.scss",
})
/**
 * Page to create an {@link app/models/activity.Activity | Activity} or {@link app/models/resource.Resource | Resource}.
 */
export class CreatePage {
  /**
   * Current entity type to create.
   * @remarks Reads from the URL queryParam "createType".
   */
  createType = input<string>();
}
