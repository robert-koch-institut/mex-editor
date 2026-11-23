import { httpResource } from "@angular/common/http";
import type { Signal } from "@angular/core";
import { computed, inject, Injectable } from "@angular/core";
import { TranslocoService } from "@jsverse/transloco";

import type { Concept } from "./models/concept";
import type { LinkLanguage, TextLanguage } from "./models/generated/shared";
import { LinkLanguageSchema, TextLanguageSchema } from "./models/generated/shared";
import type { PaginatedItemsContainer } from "./models/paginated-items-container";
import { ToLabelPipe } from "./to-label-pipe";
import { ToastNotifier } from "./toasts/toast-notifier";

/**
 * UnionType for all lookup items.
 */

/**
 * Model for NoneLookup.
 */
export interface NoneLookup<T extends undefined | null = undefined | null> {
  data: T;
  value: T;
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

@Injectable({ providedIn: "root" })
/**
 * Provides concepts as options.
 */
export class ConceptLookups {
  private transloco = inject(TranslocoService);
  // private lookupPipe = new ToLookupPipe();
  private readonly labelPipe = new ToLabelPipe();
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
    const lookups = vocabulary.items.map((x) => ({
      value: x.identifier,
      data: x,
      label: this.labelPipe.transform(x, currentLang),
    })); // this.lookupPipe.transform(x, currentLang));
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
