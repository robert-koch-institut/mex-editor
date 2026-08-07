import { httpResource } from "@angular/common/http";
import { computed, inject, Injectable } from "@angular/core";

import type { PaginatedItemsContainer } from "./models/paginated-items-container";
import { TranslocoService } from "@jsverse/transloco";
import type { Concept } from "./models/concept";
import { ToLookupPipe } from "./to-lookup-pipe";

@Injectable({ providedIn: "root" })
/**
 * Provides concepts as options.
 */
export class ConceptLookups {
  private transloco = inject(TranslocoService);
  private lookupPipe = new ToLookupPipe();

  themeOptions = this.buildConceptOptions("theme");
  resourceTypeGeneralOptions = this.buildConceptOptions("resource-type-general");
  resourceCreationMethodOptions = this.buildConceptOptions("resource-creation-method");
  frequencyOptions = this.buildConceptOptions("frequency");
  accessRestrictionOptions = this.buildConceptOptions("access-restriction");

  private buildConceptOptions(name: string) {
    const vocabReq = httpResource<PaginatedItemsContainer<Concept>>(
      () => `api/v0/vocabulary/${name}`,
      { defaultValue: { items: [], total: 0 } },
    );
    return computed(() => {
      const vocab = vocabReq.value();
      const currentLang = this.transloco.activeLang();
      const lookups = vocab.items.map((x) => this.lookupPipe.transform(x, currentLang));
      return lookups.sort((a, b) => a.label.localeCompare(b.label));
    });
  }
}
