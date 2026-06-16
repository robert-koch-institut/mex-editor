import { inject, Injectable, isDevMode } from "@angular/core";
import type { Translation, TranslocoLoader, TranslocoTestingOptions } from "@jsverse/transloco";
import { provideTransloco, TranslocoTestingModule } from "@jsverse/transloco";
import { provideTranslocoLocale } from "@jsverse/transloco-locale";
import { provideTranslocoMessageformat } from "@jsverse/transloco-messageformat";
import { HttpClient } from "@angular/common/http";
import { combineLatest, map } from "rxjs";

@Injectable({ providedIn: "root" })
export class TranslocoHttpLoader implements TranslocoLoader {
  private http = inject(HttpClient);

  getTranslation(lang: string) {
    return combineLatest([
      this.http.get<Translation>(`/i18n/model/${lang}.json`),
      this.http.get<Translation>(`/i18n/${lang}.json`),
    ]).pipe(map(([model, app]) => ({ ...model, ...app })));
  }
}

export const translocoConfig = {
  availableLangs: [
    { id: "de", label: "Deutsch" },
    { id: "en", label: "English" },
  ],
  defaultLang: "de",
  reRenderOnLangChange: true,
};

export const translocoLocaleProvider = provideTranslocoLocale({
  langToLocaleMapping: {
    de: "de-DE",
    en: "en-US",
  },
  localeToCurrencyMapping: {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    "de-DE": "EUR",
    // eslint-disable-next-line @typescript-eslint/naming-convention
    "en-US": "USD",
  },
});
export const translocoMessageformatProvider = provideTranslocoMessageformat();

export const translocoProviders = [
  provideTransloco({
    config: {
      ...translocoConfig,
      // Remove this option if your application doesn't support changing language in runtime.
      prodMode: !isDevMode(),
    },
    loader: TranslocoHttpLoader,
  }),
  translocoLocaleProvider,
  translocoMessageformatProvider,
];

/* eslint-disable @typescript-eslint/naming-convention */
const de = {
  "test.headline": "Titelzeile",
  "test.icuMessageFormat": "{count, plural, one {EINER} other {VIELE}}",
};

const en = {
  "test.headline": "Headline",
  "test.icuMessageFormat": "{count, plural, one {ONE} other {MANY}}",
};
/* eslint-enable @typescript-eslint/naming-convention */

export function getTranslocoTestingModule(options: TranslocoTestingOptions = {}) {
  const testModule = TranslocoTestingModule.forRoot({
    langs: { de, en },
    translocoConfig,
    preloadLangs: true,
    ...options,
  });
  testModule.providers?.push(translocoLocaleProvider)
  testModule.providers?.push(translocoMessageformatProvider)
  return testModule;
}
