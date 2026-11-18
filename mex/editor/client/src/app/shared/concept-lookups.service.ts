import { httpResource } from "@angular/common/http";
import type { Signal } from "@angular/core";
import { computed, inject, Injectable } from "@angular/core";
import { TranslocoService } from "@jsverse/transloco";

import type { PreviewItem } from "./models";
import type { Concept } from "./models/concept";
import type { CreateItem } from "./models/create-item";
import type { LinkLanguage, TextLanguage } from "./models/generated/shared";
import { LinkLanguageSchema, TextLanguageSchema } from "./models/generated/shared";
import type { PaginatedItemsContainer } from "./models/paginated-items-container";
import { ToLookupPipe } from "./to-lookup-pipe";
import { ToastNotifier } from "./toasts/toast-notifier";
// /**
//  * LookupItem for an empty selection.
//  */
// export interface NoneLookupItem {
//   value: null | undefined;
// }

// function hasOwnProperty<T extends object, K extends PropertyKey>(
//   obj: T,
//   key: K,
// ): obj is T & Record<K, unknown> {
//   return Object.hasOwn(obj, key);
// }

// /**
//  * Checks if the given value is a NoneLookupItem.
//  * @param value The value to check.
//  * @returns True if the given value is a NoneLookupItem; otherwise false.
//  */
// export function isNoneLookupItem(value: unknown): value is NoneLookupItem {
//   if (
//     value &&
//     typeof value === "object" &&
//     hasOwnProperty(value, "value") &&
//     [null, undefined].includes(value.value as null | undefined)
//   ) {
//     return true;
//   }
//   return false;
// }

/**
 * UnionType for all lookup items.
 */

/**
 * Model for NoneLookup.
 */
export interface NoneLookup {
  data: undefined | null;
  value: undefined | null;
  label: string;
}
/**
 * Model for ConceptLookup.
 */
export interface ConceptLookup {
  value: string;
  label: string;
  data: Concept;
}
/**
 * Model for PreviewItemLookup.
 */
export interface PreviewItemLookup {
  value: string;
  label: string;
  data: PreviewItem;
}
/**
 * Model for CreateItemLookup.
 */
export interface CreateItemLookup {
  value: string;
  label: string;
  data: CreateItem;
}
/**
 * Model for TextLanguageLookup.
 */
export interface TextLanguageLookup {
  value: TextLanguage;
  label: string;
  data: TextLanguage;
}
/**
 * Model for LinkLanguageLookup.
 */
export interface LinkLanguageLookup {
  value: LinkLanguage;
  label: string;
  data: LinkLanguage;
}

/**
 * Union type for all Lookups
 */
export type Lookup =
  | TextLanguageLookup
  | LinkLanguageLookup
  | ConceptLookup
  | PreviewItemLookup
  | CreateItemLookup
  | NoneLookup;

@Injectable({ providedIn: "root" })
/**
 * Provides concepts as options.
 */
export class ConceptLookups {
  private transloco = inject(TranslocoService);
  private lookupPipe = new ToLookupPipe();
  private notifier = inject(ToastNotifier);

  themeOptions = this.buildConceptOptions("theme");
  resourceTypeGeneralOptions = this.buildConceptOptions("resource-type-general");
  resourceCreationMethodOptions = this.buildConceptOptions("resource-creation-method");
  frequencyOptions = this.buildConceptOptions("frequency");
  accessRestrictionOptions = this.buildConceptOptions("access-restriction");
  activityTypeOptions = this.buildConceptOptions("activity-type");
  personalDataOptions = this.buildConceptOptions("personal-data");
  licenseOptions = this.buildConceptOptions("license");
  anonymizationPseudonymizationOptions = this.buildConceptOptions("anonymization-pseudonymization");
  languageOptions = this.buildConceptOptions("language");
  purposeOptions = this.buildConceptOptions("purpose");
  healthCategoryOptions = this.buildConceptOptions("health-category");
  dataProcessingStateOptions = this.buildConceptOptions("data-processing-state");

  textLanguageOptions = computed(() => {
    const lang = this.transloco.activeLang();
    return TextLanguageSchema.options.map(
      (x) =>
        ({
          label: this.transloco.translate(`language.${x}`, {}, lang),
          value: x,
          data: x,
        }) as TextLanguageLookup,
    );
  });
  linkLanguageOptions = computed(() => {
    const lang = this.transloco.activeLang();
    return LinkLanguageSchema.options.map(
      (x) =>
        ({
          label: this.transloco.translate(`language.${x}`, {}, lang),
          value: x,
          data: x,
        }) as LinkLanguageLookup,
    );
  });

  private sortedValues(vocabulary: PaginatedItemsContainer<Concept>) {
    const currentLang = this.transloco.activeLang();
    const lookups = vocabulary.items.map((x) => this.lookupPipe.transform(x, currentLang));
    return lookups.sort((a, b) => a.label.localeCompare(b.label));
  }

  private buildConceptOptions(name: string): Signal<ConceptLookup[]> {
    const vocabReq = httpResource<PaginatedItemsContainer<Concept>>(
      () => `api/v0/vocabulary/${name}`,
      { defaultValue: { items: [], total: 0 } },
    );

    return computed(() => {
      const error = vocabReq.error();
      if (error) {
        this.notifier.error(
          {
            msgKey: "errors.services.concept-lookup.loading.message",
            params: { lookupName: name },
          },
          { msgKey: "errors.services.concept-lookup.loading.title" },
          error,
        );
        const snap = vocabReq.snapshot();
        return snap.status == "resolved" ? this.sortedValues(snap.value) : [];
      }

      const vocab = vocabReq.value();
      return this.sortedValues(vocab);
    });
  }
}
