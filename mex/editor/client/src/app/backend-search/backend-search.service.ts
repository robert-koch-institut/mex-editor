import { httpResource } from "@angular/common/http";
import { Injectable, type Signal } from "@angular/core";

import type { PaginatedItemsContainer } from "../vocabulary-search/vocabulary-search.types";
import type { PreviewOrganizationalUnit, Text, UnitOption } from "./backend-search.types";

@Injectable({ providedIn: "root" })
export class BackendSearchService {
  /**
   * Search organizational units on the mex-backend as a reactive resource.
   *
   * Takes a `Signal<string>` (rather than a plain string) so the resource
   * re-fetches whenever the query changes — the basis for live search-as-you-type.
   * Must be called from an injection context, as required by `httpResource`. The URL
   * is base-href-relative so it resolves under both the dev proxy and a deployed base
   * href.
   */
  searchUnits(query: Signal<string>) {
    return httpResource<PaginatedItemsContainer<PreviewOrganizationalUnit>>(
      () =>
        `api/v0/backend/preview-item?q=${encodeURIComponent(query())}&entityType=MergedOrganizationalUnit`,
      { defaultValue: { items: [], total: 0 } },
    );
  }

  /** Map organizational units to selectable options, preferring the German name. */
  toOptions(units: PreviewOrganizationalUnit[]): UnitOption[] {
    return units.map((unit) => ({
      id: unit.identifier,
      label: this.displayName(unit.name) || unit.identifier,
    }));
  }

  /** Derive a display label from a unit's names, preferring German. */
  private displayName(name: Text[]): string {
    const german = name.find((text) => text.language === "de");
    return german?.value ?? name[0]?.value ?? "";
  }
}
