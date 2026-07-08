import { provideHttpClient, withXhr } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import { provideRouter } from "@angular/router";
import { TranslocoTestingModule } from "@jsverse/transloco";
import { translocoConfig, translocoProviders } from "./app/transloco";
// import { translocoProviders } from "./app/transloco";

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

// /**
//  * Creates the transloco testing module include all necessary providers.
//  * @param options addition option for testing purposes.
//  * @returns transloco testing module including all necessary providers.
//  */
// export function getTranslocoTestingModule(options: TranslocoTestingOptions = {}) {
//   const testModule = ;
//   const [_, ...rest] = translocoProviders;
//   testModule.providers.push(...rest);
//   return testModule;
// }
const [_, ...rest] = translocoProviders;

const testProviders = [
  provideRouter([]),
  provideHttpClient(withXhr()),
  provideHttpClientTesting(),
  TranslocoTestingModule.forRoot({
    langs: { de, en },
    translocoConfig,
    preloadLangs: true,
  }).providers,
  rest,
];

export default testProviders;
