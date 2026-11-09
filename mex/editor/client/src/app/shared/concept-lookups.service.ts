import { httpResource } from "@angular/common/http";
import { computed, inject, Injectable } from "@angular/core";
import { TranslocoService } from "@jsverse/transloco";

import type { Concept } from "./models/concept";
import type { PaginatedItemsContainer } from "./models/paginated-items-container";
import { ToLookupPipe } from "./to-lookup-pipe";
import { ToastNotifier } from "./toasts/toast-notifier";

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

  private sortedValues(vocabulary: PaginatedItemsContainer<Concept>) {
    const currentLang = this.transloco.activeLang();
    const lookups = vocabulary.items.map((x) => this.lookupPipe.transform(x, currentLang));
    return lookups.sort((a, b) => a.label.localeCompare(b.label));
  }

  private buildConceptOptions(name: string) {
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
