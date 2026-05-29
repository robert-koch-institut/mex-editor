import { AsyncPipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { Component, inject } from "@angular/core";
import { MatCardModule } from "@angular/material/card";

interface PreviewItem {
	identifier: string;
	$type: string;
}

interface PaginatedPreviewItems {
	items: PreviewItem[];
	total: number;
}

@Component({
	selector: "app-search-page",
	standalone: true,
	imports: [
		AsyncPipe,
		MatCardModule,
	],
	template: `
		<main class="main">
			<div class="page-search" aria-label="Page search">
				<input class="page-search-input" type="search" placeholder="Search..." />
				<button class="page-search-button" type="button">Search</button>
			</div>

			<h1>Search</h1>

			<section>
				@let projects = data$ | async;

				<h2>Backend Items ({{ projects?.total ?? 0 }})</h2>

				@if (!projects || (projects.items.length === 0)) {
					<p>There are no items available.</p>
				} @else {
					@for (item of projects.items; track item.identifier) {
						<mat-card class="item-card" appearance="outlined">
							<mat-card-header>
								<div class="card-header-content">
									<mat-card-subtitle>{{ item.identifier }}</mat-card-subtitle>
									<button type="button" class="toggle-btn" (click)="toggleItem(item.identifier)">
										{{ expandedItem === item.identifier ? 'hide' : 'show' }}
									</button>
								</div>
							</mat-card-header>

							@if (expandedItem === item.identifier) {
								<mat-card-content>
									<b>{{ item.identifier }}</b>
									<b>{{ item.$type }}</b>
								</mat-card-content>
							}
						</mat-card>
					}
				}
			</section>
		</main>
	`,
	styleUrl: "../app.scss",
})
export class SearchPageComponent {
	private http = inject(HttpClient);

	data$ = this.http.get<PaginatedPreviewItems>("api/v0/backend/preview-item");
	expandedItem: string | null = null;

	toggleItem(identifier: string): void {
		this.expandedItem = this.expandedItem === identifier ? null : identifier;
	}
}
