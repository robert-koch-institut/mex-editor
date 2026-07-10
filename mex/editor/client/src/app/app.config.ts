import { provideHttpClient, withXhr } from "@angular/common/http";
import type { ApplicationConfig } from "@angular/core";
import { provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";
import { translocoProviders } from "./transloco";

/**
 * Config for application.
 */
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withXhr()),
    ...translocoProviders,
  ],
};
