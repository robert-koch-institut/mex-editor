import { Component } from "@angular/core";
import { MatButton } from "@angular/material/button";
import { RouterLink } from "@angular/router";

@Component({
  selector: "mex-start-page",
  imports: [MatButton, RouterLink],
  templateUrl: "./start-page.html",
  styleUrl: "./start-page.scss",
})
/**
 * StartPage for the app.
 */
export class StartPage {}
