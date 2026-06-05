import { Component, inject } from "@angular/core";
import { MatIconModule } from "@angular/material/icon";
import { AuthService } from "../auth";

@Component({
	selector: "app-create-page",
	standalone: true,
	imports: [MatIconModule],
	template: `
		<main class="main">
			<h1>Create</h1>
      @if (authService.isLoggedIn()) {
        <p>This page is ready for your create form.</p>
      }
      @else {
        <p>Please log in to create new items.</p>
        <mat-icon aria-hidden="false" fontIcon="lock"></mat-icon>
      }
		</main>
	`,
	styles: [
		`
			.main {
				padding: 2.5rem 3rem;
			}
		`,
	],
})
export class CreatePageComponent {
  authService = inject(AuthService);
}
