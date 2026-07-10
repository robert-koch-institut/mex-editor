import type { Routes } from "@angular/router";
import { StartPage } from "./pages/start-page/start-page";
import { CreatePage } from "./pages/create-page/create-page";

/**
 * All registered Routes for the app.
 */
export const routes: Routes = [
  // The root URL now renders the StartComponent directly
  { path: "", component: StartPage },

  // Create page lives at /create
  { path: "create/:createType", component: CreatePage },

  // Optional: Redirect any unknown URLs back to the root
  { path: "**", redirectTo: "" },
];
