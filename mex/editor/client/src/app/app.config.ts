import { provideHttpClient, withXhr } from "@angular/common/http";
import type { ApplicationConfig, EnvironmentProviders, Provider } from "@angular/core";
import { inject, Injectable, provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";
import { translocoProviders } from "./transloco";
import { MAT_FORM_FIELD_DEFAULT_OPTIONS } from "@angular/material/form-field";
import {
  MAT_LUXON_DATE_ADAPTER_OPTIONS,
  provideLuxonDateAdapter,
} from "@angular/material-luxon-adapter";
import type { MatDateFormats } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { TranslocoService } from "@jsverse/transloco";

@Injectable()
class DynamicLuxonFormats implements MatDateFormats {
  private translocoService = inject(TranslocoService);

  // parse format (used for user input e.g. in date picker)
  get parse() {
    const locale = this.translocoService.getActiveLang();
    return {
      dateInput: locale === "de" ? "dd.MM.yyyy" : "MM/dd/yyyy",
    };
  }

  // Format to display dates
  get display() {
    const locale = this.translocoService.getActiveLang();
    const isDe = locale === "de";
    return {
      dateInput: isDe ? "dd.MM.yyyy" : "MM/dd/yyyy",
      monthYearLabel: "MMM yyyy",
      dateA11yLabel: "LL",
      monthYearA11yLabel: "MMMM yyyy",
    };
  }
}

/**
 * Providers for mex specific angular material default options.
 */
export const materialDefaultOptionProviders: (Provider | EnvironmentProviders)[] = [
  { provide: MAT_FORM_FIELD_DEFAULT_OPTIONS, useValue: { subscriptSizing: "dynamic" } },
  provideLuxonDateAdapter(),
  { provide: MAT_LUXON_DATE_ADAPTER_OPTIONS, useValue: { useUtc: true } },
  { provide: MAT_DATE_FORMATS, useFactory: () => new DynamicLuxonFormats() },
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
    materialDefaultOptionProviders,
  ],
};
