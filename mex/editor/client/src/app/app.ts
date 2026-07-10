import { Component } from "@angular/core";
import { RouterOutlet } from "@angular/router";
import { NavBarComponent } from "./components/nav-bar-component/nav-bar-component";
import { TranslocoDirective } from "@jsverse/transloco";

@Component({
  selector: "app-root",
  imports: [RouterOutlet, NavBarComponent, TranslocoDirective],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App {}
