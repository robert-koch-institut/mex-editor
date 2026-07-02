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

  onClick() {
    console.warn("CLICKED");
  }
}
