import { isDevMode } from "@angular/core";
import type { Routes } from "@angular/router";

import { FastTrackActivity } from "./fast-track/fast-track-activity/fast-track-activity";
import { FastTrackResource } from "./fast-track/fast-track-resource/fast-track-resource";
import { StartPage } from "./start-page/start-page";

/**
 * All routes for the app.
 */
const appRoutes: Routes = [
  { path: "", component: StartPage },

  { path: "create/activity", component: FastTrackActivity },
  { path: "create/resource", component: FastTrackResource },
];

/**
 * Dev routes (only availble in dev mode) for the app.
 */
const devRoutes: Routes = [
  {
    path: "dev/figma-test",
    loadComponent: () => import("./figma-test-page/figma-test-page").then((m) => m.FigmaTestPage),
  },
];

/**
 * All registered Routes for the app.
 */
export const routes: Routes = [
  ...appRoutes,
  ...(isDevMode() ? devRoutes : []), // Optional: Redirect any unknown URLs back to the root
  ...[{ path: "**", redirectTo: "" }],
];
