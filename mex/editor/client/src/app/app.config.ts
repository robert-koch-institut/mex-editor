import { provideHttpClient, withXhr } from "@angular/common/http";
import type { ApplicationConfig, EnvironmentProviders, Provider } from "@angular/core";
import {
  inject,
  Injectable,
  provideAppInitializer,
  provideBrowserGlobalErrorListeners,
} from "@angular/core";
import type { MatDateFormats } from "@angular/material/core";
import { MAT_DATE_FORMATS } from "@angular/material/core";
import { MAT_FORM_FIELD_DEFAULT_OPTIONS } from "@angular/material/form-field";
import {
  MAT_LUXON_DATE_ADAPTER_OPTIONS,
  provideLuxonDateAdapter,
} from "@angular/material-luxon-adapter";
import { provideRouter, withComponentInputBinding } from "@angular/router";
import { TranslocoService } from "@jsverse/transloco";
import z from "zod";

import { routes } from "./app.routes";
import { translocoProviders } from "./transloco";

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
  provideLuxonDateAdapter(),
  { provide: MAT_FORM_FIELD_DEFAULT_OPTIONS, useValue: { subscriptSizing: "dynamic" } },
  { provide: MAT_LUXON_DATE_ADAPTER_OPTIONS, useValue: { useUtc: true } },
  { provide: MAT_DATE_FORMATS, useFactory: () => new DynamicLuxonFormats() },
];

/**
 * Provider to initialize Zod.
 */
export const zodInitProvider = provideAppInitializer(() => {
  z.config({
    // eslint-disable-next-line complexity
    customError: (iss) => {
      switch (iss.code) {
        case "invalid_type":
          return "validation.invalidType";

        case "too_small":
          switch (iss.origin) {
            case "string":
              return "validation.minLength";
            case "array":
              return "validation.minItems";
            case "number":
            case "int":
            case "bigint":
              return "validation.min";
            case "date":
              return "validation.minDate";
            default:
              return "validation.tooSmall";
          }

        case "too_big":
          switch (iss.origin) {
            case "string":
              return "validation.maxLength";
            case "array":
              return "validation.maxItems";
            case "number":
            case "int":
            case "bigint":
              return "validation.max";
            case "date":
              return "validation.maxDate";
            default:
              return "validation.tooBig";
          }

        case "invalid_format":
          return `validation.invalidFormat.${iss.format}`;

        case "not_multiple_of":
          return "validation.notMultipleOf";

        case "unrecognized_keys":
          return "validation.unrecognizedKeys";

        case "invalid_union":
          return "validation.invalidUnion";

        case "invalid_key":
          return "validation.invalidKey";

        case "invalid_element":
          return "validation.invalidElement";

        case "invalid_value":
          return "validation.invalidValue";

        case "custom":
          return "validation.custom";

        default:
          return "validation.generic";
      }
    },
  });
});

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
    zodInitProvider,
  ],
};
