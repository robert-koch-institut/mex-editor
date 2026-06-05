import { Component, inject } from "@angular/core";
import { MatIconModule } from "@angular/material/icon";
import { AuthService } from "../auth";

@Component({
	selector: "app-edit-page",
	standalone: true,
  imports: [MatIconModule],
	template: `
		<main class="main">
			<h1>Edit</h1>
			@if (authService.isLoggedIn()) {
        <p>This page is ready for your edit form.</p>
      }
      @else {
        <p>Please log in to edit items.</p>
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
export class EditPageComponent {
  authService = inject(AuthService);
}
