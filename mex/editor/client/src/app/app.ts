import type { OnInit } from "@angular/core";
import { Component, DestroyRef, inject } from "@angular/core";
import { ActivatedRoute, Router, RouterOutlet } from "@angular/router";
import { NavBarComponent } from "./components/nav-bar-component/nav-bar-component";
import { TranslocoDirective, TranslocoService } from "@jsverse/transloco";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";

@Component({
  selector: "app-root",
  imports: [RouterOutlet, NavBarComponent, TranslocoDirective],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App implements OnInit {
  private transloco = inject(TranslocoService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private destroyRef = inject(DestroyRef);

  ngOnInit() {
    // Whenever the language changes, update the query parameter
    this.transloco.langChanges$.pipe(takeUntilDestroyed(this.destroyRef)).subscribe((lang) => {
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { language: lang },
        queryParamsHandling: "merge", // Keep other existing params
      });
    });
  }
}
