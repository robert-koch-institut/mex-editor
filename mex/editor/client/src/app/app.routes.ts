import type { Routes } from "@angular/router";

import { FastTrackActivity } from "./fast-track/fast-track-activity/fast-track-activity";
import { FastTrackResource } from "./fast-track/fast-track-resource/fast-track-resource";
import { FigmaTestPage } from "./figma-test-page/figma-test-page";
import { StartPage } from "./start-page/start-page";

/**
 * All registered Routes for the app.
 */
export const routes: Routes = [
  // The root URL now renders the StartComponent directly
  { path: "", component: StartPage },

  { path: "create/activity", component: FastTrackActivity },
  { path: "create/resource", component: FastTrackResource },

  { path: "figma-test", component: FigmaTestPage },

  // Optional: Redirect any unknown URLs back to the root
  { path: "**", redirectTo: "" },
];
