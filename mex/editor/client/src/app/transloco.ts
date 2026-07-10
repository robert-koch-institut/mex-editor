import { inject, Injectable, isDevMode, provideAppInitializer } from "@angular/core";
import type { Translation, TranslocoLoader } from "@jsverse/transloco";
import { provideTransloco, TranslocoService } from "@jsverse/transloco";
import { provideTranslocoLocale } from "@jsverse/transloco-locale";
import { provideTranslocoMessageformat } from "@jsverse/transloco-messageformat";
import { HttpClient } from "@angular/common/http";
import { combineLatest, filter, map } from "rxjs";
import type { GetLangParams } from "@jsverse/transloco-persist-lang";
import { provideTranslocoPersistLang } from "@jsverse/transloco-persist-lang";
import { NavigationEnd, Router } from "@angular/router";

/**
 * Name of the language query param.
 */
export const LANGUAGE_QUERY_PARAM = "language";

/**
 * TranslocoLoader using HTTP to load translation jsons.
 * @see {@link https://jsverse.gitbook.io/transloco/getting-started/installation#transloco-loader}
 */
@Injectable({ providedIn: "root" })
class TranslocoHttpLoader implements TranslocoLoader {
  private http = inject(HttpClient);

  getTranslation(lang: string) {
    return combineLatest([
      this.http.get<Translation>(`api/v0/i18n/${lang}`),
      this.http.get<Translation>(`/i18n/${lang}.json`),
    ]).pipe(map(([model, app]) => ({ ...model, ...app })));
  }
}

/**
 * Base config for transloco.
 */
export const translocoConfig = {
  availableLangs: [
    { id: "de", label: "Deutsch" },
    { id: "en", label: "English" },
  ],
  defaultLang: "de",
  reRenderOnLangChange: true,
};

/**
 * Transloco locale provider to use pipes that depend on the active language,
 * including mappings for lang to locale and locale to currency.
 * @see {@link https://jsverse.gitbook.io/transloco/plugins-and-extensions/locale-l10n#setup}
 */
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

/**
 * Factory to create a transloco storage for {@link LANGUAGE_QUERY_PARAM} query param.
 * @returns transloco storage {@link https://jsverse.gitbook.io/transloco/plugins-and-extensions/persist-lang} for query param.
 */
function queryParamStorage() {
  const router = inject(Router);
  return {
    getItem(_key: string): string | null {
      return router.routerState.snapshot.root.queryParamMap.get(LANGUAGE_QUERY_PARAM);
    },
    setItem(_key: string, value: string): void {
      router.navigate([], {
        queryParams: { [LANGUAGE_QUERY_PARAM]: value },
        queryParamsHandling: "merge",
      });
    },
    removeItem(_key: string): void {
      router.navigate([], {
        queryParams: { [LANGUAGE_QUERY_PARAM]: null },
        queryParamsHandling: "merge",
      });
    },
  };
}

/**
 * Factory to create a transloco storage for html language attribute.
 * @returns transloco storage {@link https://jsverse.gitbook.io/transloco/plugins-and-extensions/persist-lang} for html language attribute.
 */
function htmlLangAttributeStorage() {
  return {
    getItem(_key: string): string | null {
      return document.documentElement.getAttribute("lang");
    },
    setItem(_key: string, value: string): void {
      document.documentElement.setAttribute("lang", value);
    },
    removeItem(_key: string): void {
      document.documentElement.removeAttribute("lang");
    },
  };
}

/**
 * Factory that creates a combinated transloco storage for query param and html lang attribute.
 * @returns Combined query param and html lang attribute storage.
 */
function mexEditorTranslocoStorage() {
  const queryStorage = queryParamStorage();
  const htmlStorage = htmlLangAttributeStorage();
  return {
    getItem(_key: string): string | null {
      return queryStorage.getItem(_key) ?? localStorage.getItem(_key);
    },
    setItem(_key: string, value: string): void {
      htmlStorage.setItem(_key, value);
      queryStorage.setItem(_key, value);
      localStorage.setItem(_key, value);
    },
    removeItem(_key: string): void {
      htmlStorage.removeItem(_key);
      queryStorage.removeItem(_key);
      localStorage.removeItem(_key);
    },
  };
}

/**
 * Function to determin the default language on startup for transloco.
 * Checks if the {@link LANGUAGE_QUERY_PARAM} QueryParam is present in the url and parses it or using the default language.
 * @param param0 transloco default language.
 * @returns The determined default language for transloco.
 */
export function getLangFn({ cachedLang, defaultLang }: GetLangParams) {
  // const urlParams = new URLSearchParams(window.location.search);
  // const urlLang = urlParams.get(LANGUAGE_QUERY_PARAM);

  // Return URL language if present, otherwise default
  return cachedLang || defaultLang;
}

/**
 * PersitentLangProvider using QueryParams.
 * @see {@link https://jsverse.gitbook.io/transloco/plugins-and-extensions/persist-lang}
 */
const translocoPersistLangProvider = provideTranslocoPersistLang({
  getLangFn,
  storage: { useFactory: mexEditorTranslocoStorage },
  storageKey: "mex_editor_language",
});

/**
 * Factory for creating an app initializer that syncs url changes that include the {@link LANGUAGE_QUERY_PARAM} QueryParam with the {@link @jsverse/transloco.TranslocoService} and sets it active language.
 * @returns An app initializer that syncs language url query param with
 */
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

const queryParamSyncProvider = provideQueryParamTranslocoSync();

/**
 * All providers to use transloco as main translation framework.
 */
export const translocoProviders = [
  provideTransloco({
    config: {
      ...translocoConfig,
      prodMode: !isDevMode(),
    },
    loader: TranslocoHttpLoader,
  }),
  translocoLocaleProvider,
  translocoMessageformatProvider,
  translocoPersistLangProvider,
  queryParamSyncProvider,
];
