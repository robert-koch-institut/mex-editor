import { provideHttpClient, withXhr } from "@angular/common/http";
import type { ApplicationConfig, EnvironmentProviders, Provider } from "@angular/core";
import { inject, Injectable, provideBrowserGlobalErrorListeners } from "@angular/core";
import { provideRouter, withComponentInputBinding } from "@angular/router";

import { routes } from "./app.routes";
import { translocoProviders } from "./transloco";
import { MAT_FORM_FIELD_DEFAULT_OPTIONS } from "@angular/material/form-field";
import { provideLuxonDateAdapter } from "@angular/material-luxon-adapter";
import type { MatDateFormats } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { TranslocoService } from "@jsverse/transloco";

@Injectable()
class DynamicLuxonFormats implements MatDateFormats {
  private dateAdapter = inject(TranslocoService);

  // Das Parse-Format (wichtig für manuelle Tastatureingaben des Users)
  get parse() {
    const locale = this.dateAdapter.getActiveLang();
    return {
      dateInput: locale === "de" ? "dd.MM.yyyy" : "MM/dd/yyyy",
    };
  }

  // Das Anzeige-Format im Inputfeld und Kalender-Labels
  get display() {
    const locale = this.dateAdapter.getActiveLang();
    const isDe = locale === "de";
    return {
      dateInput: isDe ? "dd.MM.yyyy" : "MM/dd/yyyy",
      monthYearLabel: isDe ? "MMM yyyy" : "MMM yyyy",
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
  { provide: MAT_DATE_FORMATS, useFactory: () => new DynamicLuxonFormats() },
  provideLuxonDateAdapter(),
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
