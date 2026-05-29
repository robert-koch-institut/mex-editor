import { Component } from "@angular/core";

@Component({
	selector: "app-edit-page",
	standalone: true,
	template: `
		<main class="main">
			<h1>Edit</h1>
			<p>This page is ready for your edit form.</p>
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
export class EditPageComponent {}
