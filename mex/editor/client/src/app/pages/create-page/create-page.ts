import { Component, input } from "@angular/core";

@Component({
  selector: "app-create-page",
  imports: [],
  templateUrl: "./create-page.html",
  styleUrl: "./create-page.scss",
})
export class CreatePage {
  createType = input<string>();

}
