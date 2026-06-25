import { AsyncPipe } from "@angular/common";
import { Component, inject, signal } from "@angular/core";
import { MatButton } from "@angular/material/button";
import { RouterLink } from "@angular/router";
import { BackendProxyService } from "../../services/backend-proxy-service";

/**
 * Startpage including a welcome and navigation to create page.
 */
@Component({
  selector: "app-start-page",
  imports: [RouterLink, AsyncPipe, MatButton],
  templateUrl: "./start-page.html",
  styleUrl: "./start-page.scss",
})
export class StartPage {
  protected readonly title = signal("mex-editor-ng");
  protected readonly backendProxy = inject(BackendProxyService);

  /** Data to showcase preview items from backend proxy. */
  data$ = this.backendProxy.getPreviewItems();
}
