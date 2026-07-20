import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { NavBar } from "./nav-bar/nav-bar";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "mex-root",
  imports: [RouterOutlet, NavBar, TranslocoDirective],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
/**
 * The EntryPoint-Component for the angular app.
 */
export class App {}
