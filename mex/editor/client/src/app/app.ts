import { Component } from "@angular/core";
import { MatIcon } from "@angular/material/icon";
import { RouterOutlet } from "@angular/router";
import { NavBarComponent } from "./components/nav-bar-component/nav-bar-component";
import { TranslocoDirective } from "@jsverse/transloco";
import { AsyncPipe } from "@angular/common";


@Component({
  selector: "app-root",
  imports: [
    RouterOutlet,
    MatIcon,
    NavBarComponent,
    TranslocoDirective,
    AsyncPipe
],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App {
}
