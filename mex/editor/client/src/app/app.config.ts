import { provideHttpClient, withXhr } from "@angular/common/http";
import type { ApplicationConfig, EnvironmentProviders, Provider } from "@angular/core";
import { provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";
import { translocoProviders } from "./transloco";
import { MAT_FORM_FIELD_DEFAULT_OPTIONS } from "@angular/material/form-field";

const materialDefaultOptions: (Provider | EnvironmentProviders)[] = [
  { provide: MAT_FORM_FIELD_DEFAULT_OPTIONS, useValue: { subscriptSizing: "dynamic" } },
];

/**
 * Config for application.
 */
export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideHttpClient(withXhr()),
    provideRouter(routes, withComponentInputBinding()),
    translocoProviders,
    materialDefaultOptions,
  ],
};
