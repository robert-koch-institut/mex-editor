import type { Routes } from "@angular/router";
import { CreatePageComponent } from "./pages/create-page";
import { SearchPageComponent } from "./pages/search-page";
import { EditPageComponent } from "./pages/edit-page";

export const routes: Routes = [
  {
    path: "",
    pathMatch: "full",
    redirectTo: "search",
  },
  {
    path: "search",
    component: SearchPageComponent,
  },
  {
    path: "create",
    component: CreatePageComponent,
  },
  {
    path: "edit",
    component: EditPageComponent,
  },
  {
    path: "**",
    redirectTo: "search",
  },
];
