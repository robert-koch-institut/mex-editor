import type { Routes } from "@angular/router";
import { StartPage } from "./pages/start-page/start-page";
import { FastTrackActivity } from "./fast-track-activity/fast-track-activity";

export const routes: Routes = [
  // The root URL now renders the StartComponent directly
  { path: '', component: StartPage },

  { path: 'create/activity', component: FastTrackActivity },

  // Optional: Redirect any unknown URLs back to the root
  { path: '**', redirectTo: '' }
];
