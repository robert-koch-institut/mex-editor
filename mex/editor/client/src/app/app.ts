import { Component } from "@angular/core";
import { MatIcon } from "@angular/material/icon";
import { RouterOutlet } from "@angular/router";
import { NavBar } from "./nav-bar/nav-bar";

@Component({
  selector: "mex-root",
  imports: [RouterOutlet, MatIcon, NavBar],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App {}
