import type { Routes } from "@angular/router";
import { CreatePageComponent } from "./pages/create-page";
import { SearchPageComponent } from "./pages/search-page";
import { EditPageComponent } from "./pages/edit-page";
import { ProjectDetailComponent } from "./pages/project-detail";
import { MitarbeiterDetailComponent } from "./pages/mitarbeiter-detail";

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
    path: "edit/:id",
    component: EditPageComponent,
  },
  {
    path: "projekte/:id",
    component: ProjectDetailComponent,
    children: [
      {
        path: "mitarbeiter/:mid",
        component: MitarbeiterDetailComponent,
      },
    ],
  },
  {
    path: "**",
    redirectTo: "search",
  },
];
