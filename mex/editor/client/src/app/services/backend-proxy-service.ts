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
 * Model for mex.backend PaginatedPreviewItems.
 */
export interface PaginatedPreviewItems {
  items: PreviewItem[];
  total: number;
}

/**
 * A service to read items from the mex.backend using the fastapi backend proxy endpoint.
 */
@Injectable({
  providedIn: "root",
})
export class BackendProxyService {
  private _http = inject(HttpClient);

  /**
   * Get PreviewItems by its corrosponding endpoint.
   * @returns PreviewItems with pagination metadata.
   */
  getPreviewItems(): Observable<PaginatedPreviewItems> {
    return this._http.get<PaginatedPreviewItems>("api/v0/backend/preview-item");
  }
}
