import { Component } from "@angular/core";
import { MatIcon } from "@angular/material/icon";
import { RouterOutlet } from "@angular/router";
import { NavBarComponent } from "./components/nav-bar-component/nav-bar-component";

/**
 * The EntryPoint-Component for the angular app.
 */
@Component({
  selector: "app-root",
  imports: [
    RouterOutlet,
    MatIcon,
    NavBarComponent
  ],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App {

}
