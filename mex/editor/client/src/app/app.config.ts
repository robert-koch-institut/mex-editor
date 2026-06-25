import { provideHttpClient } from "@angular/common/http";
import type { ApplicationConfig } from "@angular/core";
import { provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";

/** Routerprovider with activated component input binding. */
export const routerProvider = provideRouter(routes, withComponentInputBinding());

export const appConfig: ApplicationConfig = {
  providers: [provideBrowserGlobalErrorListeners(), routerProvider, provideHttpClient()],
};
