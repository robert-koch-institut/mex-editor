import { Component, input } from "@angular/core";

/**
 * Page to create an {@link app/models/activity.Activity | Activity} or {@link app/models/resource.Resource | Resource}.
 */
@Component({
  selector: "app-create-page",
  imports: [],
  templateUrl: "./create-page.html",
  styleUrl: "./create-page.scss",
})
export class CreatePage {
  /**
   * Current entity type to create.
   * @remarks Get read from the URL queryParam "createType".
   * @see {@link "app/app.config".routerProvider | routerProvider} for more informations.
   */
  createType = input<string>();
}
