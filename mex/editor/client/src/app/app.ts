import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { TranslocoDirective } from "@jsverse/transloco";

import { Resource } from "./create/resource/resource";
import { NavBar } from "./nav-bar/nav-bar";

@Component({
  selector: "mex-root",
  imports: [NavBar, Resource, RouterOutlet, TranslocoDirective],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
/**
 * The EntryPoint-Component for the angular app.
 */
export class App {}
