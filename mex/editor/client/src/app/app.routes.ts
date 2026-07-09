import type { Routes } from "@angular/router";
import { CreatePageComponent } from "./pages/create-page";
import { SearchPageComponent } from "./pages/search-page";
import { EditPageComponent } from "./pages/edit-page";
import { ProjectDetailComponent } from "./pages/project-detail";
import { MitarbeiterDetailComponent } from "./pages/mitarbeiter-detail";
import { authGuard } from "./auth-guard";

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
    canActivate: [authGuard],
  },
  {
    path: "edit",
    component: EditPageComponent,
    canActivate: [authGuard],
  },
  {
    path: "edit/:id",
    component: EditPageComponent,
    canActivate: [authGuard],
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
