import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import type { Observable } from "rxjs";

/**
 * Model for mex.backend PreviewItem.
 */
export interface PreviewItem {
  identifier: string;
  $type: string;
}

/**
 * Model for mex.backend PaginatedItemContainer.
 */
export interface PaginatedItemContainer<T> {
  items: T[];
  total: number;
}

@Injectable({
  providedIn: "root",
})
/**
 * A service to read items from the mex.backend using the fastapi backend proxy endpoint.
 */
export class BackendProxyService {
  private _http = inject(HttpClient);

  /**
   * Get PreviewItems by its corrosponding endpoint.
   * @returns PreviewItems with pagination metadata.
   */
  getPreviewItems(): Observable<PaginatedItemContainer<PreviewItem>> {
    return this._http.get<PaginatedItemContainer<PreviewItem>>("api/v0/backend/preview-item");
  }
}
