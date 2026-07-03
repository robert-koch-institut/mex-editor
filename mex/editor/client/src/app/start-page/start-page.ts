import { Component } from "@angular/core";
import { MatButton } from "@angular/material/button";
import { RouterLink } from "@angular/router";

@Component({
  selector: "mex-start-page",
  imports: [RouterLink, MatButton],
  templateUrl: "./start-page.html",
  styleUrl: "./start-page.scss",
})
export class StartPage {
}
