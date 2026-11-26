import { isDevMode } from "@angular/core";
import type { Routes } from "@angular/router";

import { CreateResource } from "./create/create-resource/create-resource";
import { Edit } from "./edit/edit";
import { FastTrackActivity } from "./fast-track/fast-track-activity/fast-track-activity";
import { FastTrackResource } from "./fast-track/fast-track-resource/fast-track-resource";
import { StartPage } from "./start-page/start-page";

/**
 * All routes for the app.
 */
const appRoutes: Routes = [
  { path: "", component: StartPage },

  { path: "fasttrack/activity", component: FastTrackActivity },
  { path: "fasttrack/resource", component: FastTrackResource },

  {
    path: "create/resource",
    children: [
      { path: "", redirectTo: "general", pathMatch: "full" },
      { path: ":step", component: CreateResource },
    ],
  },

  { path: "edit/:entityId", component: Edit },
];

/**
 * Dev routes (only available in dev mode) for the app.
 */
const devRoutes: Routes = [
  {
    path: "dev/figma-test",
    loadComponent: () => import("./figma-test-page/figma-test-page").then((m) => m.FigmaTestPage),
  },
  {
    path: "dev/zod-control-test",
    loadComponent: () =>
      import("./create/test-generic-zod-control/test-generic-zod-control").then(
        (m) => m.TestGenericZodControl,
      ),
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
