import { httpResource } from "@angular/common/http";
import { computed, inject, Injectable } from "@angular/core";

import type { BilingualText, Concept } from "./concept-options.types";
import type { PaginatedItemsContainer } from "../shared/models/paginated-items-container";
import { TranslocoService } from "@jsverse/transloco";

@Injectable({ providedIn: "root" })
/**
 * Provides concepts as options.
 */
export class ConceptOptions {
  private transloco = inject(TranslocoService);

  themeOptions = this.buildConceptOptions("theme");
  resourceTypeGeneralOptions = this.buildConceptOptions("resource-type-general");
  resourceCreationMethodOptions = this.buildConceptOptions("resource-creation-method");
  accrualPeriodicityOptions = this.buildConceptOptions("frequency");
  accessRestrictionOptions = this.buildConceptOptions("access-restriction");

  private getConceptLabel(concept: Concept, currentLang: string) {
    const getTextLabel = (text: BilingualText) => {
      const key = currentLang as keyof BilingualText;
      if (key in text && text[key]) {
        return text[key];
      }
      return undefined;
    };
    return (
      getTextLabel(concept.prefLabel) || concept.altLabel.map(getTextLabel)[0] || concept.identifier
    );
  }

  private conceptsToOptions(concepts: Concept[], currentLang: string) {
    const options = concepts.map((concept) => ({
      id: concept.identifier,
      label: this.getConceptLabel(concept, currentLang),
    }));

    return options.sort((a, b) => a.label.localeCompare(b.label));
  }

  private buildConceptOptions(name: string) {
    const vocabReq = httpResource<PaginatedItemsContainer<Concept>>(
      () => `api/v0/vocabulary/${name}`,
      { defaultValue: { items: [], total: 0 } },
    );
    return computed(() => {
      const vocab = vocabReq.value();
      const currentLang = this.transloco.activeLang();
      return this.conceptsToOptions(vocab.items, currentLang);
    });
  }
}
