import { provideHttpClient, withXhr } from "@angular/common/http";
import { provideHttpClientTesting } from "@angular/common/http/testing";
import { signal } from "@angular/core";
import { provideRouter } from "@angular/router";
import { TranslocoTestingModule } from "@jsverse/transloco";

import { materialDefaultOptionProviders } from "./app/app.config";
import { ConceptLookups } from "./app/shared/concept-lookups.service";
import { translocoConfig, translocoProviders } from "./app/transloco";

/* eslint-disable @typescript-eslint/naming-convention */
const de = {
  "test.headline": "Titelzeile",
  "test.icuMessageFormat": "{count, plural, one {EINER} other {VIELE}}",
  "test.fieldset.label": "deutsches label",
};

const en = {
  "test.headline": "Headline",
  "test.icuMessageFormat": "{count, plural, one {ONE} other {MANY}}",
  "test.fieldset.label": "english label",
};
/* eslint-enable @typescript-eslint/naming-convention */

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
  materialDefaultOptionProviders,
  {
    provide: ConceptLookups,
    useValue: {
      themeOptions: signal([
        { id: "theme-1", label: "1. Theme" },
        { id: "theme-2", label: "2. Theme" },
      ]),
      resourceTypeGeneralOptions: signal([
        { id: "resourceTypeGeneral-1", label: "1. ResourceTypeGeneral" },
        { id: "resourceTypeGeneral-2", label: "2. ResourceTypeGeneral" },
      ]),
      resourceCreationMethodOptions: signal([
        { id: "resourceCreationMethod-1", label: "1. ResourceCreationMethod" },
        { id: "resourceCreationMethod-2", label: "2. ResourceCreationMethod" },
      ]),
      frequencyOptions: signal([
        { id: "frequency-1", label: "1. Frequency" },
        { id: "frequency-2", label: "2. Frequency" },
      ]),
      accessRestrictionOptions: signal([
        { id: "accessRestriction-1", label: "1. AccessRestriction" },
        { id: "accessRestriction-2", label: "2. AccessRestriction" },
      ]),
    },
  },
];

export default testProviders;
