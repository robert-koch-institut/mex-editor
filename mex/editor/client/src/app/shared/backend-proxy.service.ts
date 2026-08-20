import { HttpClient, httpResource } from "@angular/common/http";
import { inject, Injectable, type Signal } from "@angular/core";
import type { Observable } from "rxjs";

import type { PreviewOrganizationalUnit } from "./models/generated/organizational-unit";
import type { PaginatedItemsContainer } from "./models/paginated-items-container";

@Injectable({ providedIn: "root" })
/**
 * Service to search for entites in the backend.
 */
export class BackendProxy {
  private _http = inject(HttpClient);
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

  /**
   * Get PreviewItems by its corrosponding endpoint.
   * @returns PreviewItems with pagination metadata.
   */
  getPreviewItems(): Observable<PaginatedItemsContainer<{ $type: string; identifier: string }>> {
    return this._http.get<PaginatedItemsContainer<{ $type: string; identifier: string }>>(
      "api/v0/backend/preview-item",
    );
  }
}
