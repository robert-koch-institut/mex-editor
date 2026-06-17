import { inject, Injectable, isDevMode, provideAppInitializer } from "@angular/core";
import type { Translation, TranslocoLoader, TranslocoTestingOptions } from "@jsverse/transloco";
import { provideTransloco, TranslocoService, TranslocoTestingModule } from "@jsverse/transloco";
import { provideTranslocoLocale } from "@jsverse/transloco-locale";
import { provideTranslocoMessageformat } from "@jsverse/transloco-messageformat";
import { HttpClient } from "@angular/common/http";
import { combineLatest, filter, map } from "rxjs";
import type { GetLangParams } from "@jsverse/transloco-persist-lang";
import { provideTranslocoPersistLang } from "@jsverse/transloco-persist-lang";
import { NavigationEnd, Router } from "@angular/router";

export const LANGUAGE_QUERY_PARAM  = "language"

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

export const translocoConfig = {
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

function queryParamStorage() {
  const router = inject(Router);
  return {
    getItem(_key: string): string | null {
      return router.routerState.snapshot.root.queryParamMap.get(LANGUAGE_QUERY_PARAM);
    },
    setItem(_key: string, value: string): void {
      router.navigate([], { queryParams: { [LANGUAGE_QUERY_PARAM]: value }, queryParamsHandling: "merge" });
    },
    removeItem(_key: string): void {
      router.navigate([], { queryParams: { [LANGUAGE_QUERY_PARAM]: null }, queryParamsHandling: "merge" });
    },
  };
}

export function getLangFn({ defaultLang }: GetLangParams) {
  const urlParams = new URLSearchParams(window.location.search);
  const urlLang = urlParams.get(LANGUAGE_QUERY_PARAM);

  // Return URL lang if present, otherwise default
  return urlLang || defaultLang;
}

const translocoPersistLangProvider = provideTranslocoPersistLang({
  getLangFn,
  storage: { useFactory: queryParamStorage }, // Also save to localStorage as backup
});


export function provideQueryParamTranslocoSync() {
  return provideAppInitializer(() => {
    const router = inject(Router);
    const transloco = inject(TranslocoService);

    // 1. URL -> activeLang
    // Fires on every completed navigation, including the initial one.
    router.events
      .pipe(filter((e): e is NavigationEnd => e instanceof NavigationEnd))
      .subscribe(() => {
        const urlLang = router.routerState.snapshot.root.queryParamMap.get(LANGUAGE_QUERY_PARAM);
        const availableLangs = transloco
          .getAvailableLangs()
          .map((l) => (typeof l === "string" ? l : l.id));

        if (urlLang && availableLangs.includes(urlLang) && urlLang !== transloco.getActiveLang()) {
          transloco.setActiveLang(urlLang);
        }
      });
  });
}

const queryParamSyncProvider = provideQueryParamTranslocoSync()

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
  queryParamSyncProvider
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
  testModule.providers?.push(translocoPersistLangProvider);
  testModule.providers?.push(queryParamSyncProvider);
  return testModule;
}
