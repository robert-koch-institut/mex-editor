import { inject, Injectable, isDevMode } from "@angular/core";
import type { Translation, TranslocoLoader, TranslocoTestingOptions } from "@jsverse/transloco";
import { provideTransloco, TranslocoTestingModule } from "@jsverse/transloco";
import { provideTranslocoLocale } from "@jsverse/transloco-locale";
import { provideTranslocoMessageformat } from "@jsverse/transloco-messageformat";
import { HttpClient } from "@angular/common/http";
import { combineLatest, map } from "rxjs";
import type { GetLangParams } from "@jsverse/transloco-persist-lang";
import { provideTranslocoPersistLang } from "@jsverse/transloco-persist-lang";

@Injectable({ providedIn: "root" })
class TranslocoHttpLoader implements TranslocoLoader {
  private http = inject(HttpClient);

  getTranslation(lang: string) {
    return combineLatest([
      this.http.get<Translation>(`/i18n/model/${lang}.json`),
      this.http.get<Translation>(`/i18n/${lang}.json`),
    ]).pipe(map(([model, app]) => ({ ...model, ...app })));
  }
}

const translocoConfig = {
  availableLangs: [
    { id: "de", label: "Deutsch" },
    { id: "en", label: "English" },
  ],
  defaultLang: "de",
  reRenderOnLangChange: true,
};

const translocoLocaleProvider = provideTranslocoLocale({
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
const translocoMessageformatProvider = provideTranslocoMessageformat();

export function getLangFn({ defaultLang }: GetLangParams) {
  const urlParams = new URLSearchParams(window.location.search);
  const urlLang = urlParams.get("language");

  // Return URL lang if present, otherwise default
  return urlLang || defaultLang;
}

const translocoPersistLangProvider = provideTranslocoPersistLang({
  getLangFn,
  storage: { useValue: localStorage }, // Also save to localStorage as backup
});

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
  translocoPersistLangProvider,
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
  testModule.providers?.push(translocoLocaleProvider);
  testModule.providers?.push(translocoMessageformatProvider);
  return testModule;
}
