import { Component } from "@angular/core";

@Component({
	selector: "app-create-page",
	standalone: true,
	template: `
		<main class="main">
			<h1>Create</h1>
			<p>This page is ready for your create form.</p>
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
export class CreatePageComponent {}
