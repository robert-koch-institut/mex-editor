import { httpResource } from "@angular/common/http";
import { Injectable } from "@angular/core";

import type { Concept, PaginatedItemsContainer, VocabularyOption } from "./vocabulary-search.types";

@Injectable({ providedIn: "root" })
export class VocabularySearchService {
  /**
   * Fetch a vocabulary by its name as a reactive resource.
   *
   * Must be called from an injection context (e.g. a component field initializer),
   * as required by `httpResource`. The URL is base-href-relative so it resolves
   * correctly under both the dev proxy and a deployed base href.
   */
  getVocabulary(name: string) {
    return httpResource<PaginatedItemsContainer<Concept>>(() => `api/v0/vocabulary/${name}`, {
      defaultValue: { items: [], total: 0 },
    });
  }

  /** Map concepts to selectable options, preferring the German label. */
  toOptions(concepts: Concept[]): VocabularyOption[] {
    return concepts.map((concept) => ({
      id: concept.identifier,
      label: concept.prefLabel.de ?? concept.prefLabel.en ?? concept.identifier,
    }));
  }
}
