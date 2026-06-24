import { AsyncPipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { Component, inject, signal } from "@angular/core";
import { MatButton } from "@angular/material/button";
import { RouterLink } from "@angular/router";

interface PreviewItem {
  identifier: string;
  $type: string;
}

interface PaginatedPreviewItems {
  items: PreviewItem[];
  total: number;
}

/**
 * A Component for the Startpage
 */
@Component({
  selector: "app-start-page",
  imports: [RouterLink, AsyncPipe, MatButton],
  templateUrl: "./start-page.html",
  styleUrl: "./start-page.scss",
})
export class StartPage {
  protected readonly title = signal("mex-editor-ng");
  private http = inject(HttpClient);

  data$ = this.http.get<PaginatedPreviewItems>("api/v0/backend/preview-item");

  onClick(): void {
    console.warn("CLICKED");
  }

  /**
   * This fucntion does something!
   * @param arg1 this arg is a string and is important
   * @param arg2 this arg is a number and is less important
   * @returns A boolean array that say basicly nothing :E
   */
  doSth(arg1: string, arg2: number): boolean[] {
    return [!!arg1 || !!arg2];
  }
}
