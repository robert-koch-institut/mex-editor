import { AsyncPipe, DatePipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { Component, inject } from "@angular/core";
import { MatCardModule } from "@angular/material/card";
import { MatListModule } from "@angular/material/list";
import { RouterLink } from "@angular/router";
import { DummyDataService } from "../services/dummy-data.service";
import type { Project } from "../models/project.model";

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
    DatePipe,
		MatCardModule,
		MatListModule,
		RouterLink,
	],
	template: `
		<main class="main">
			<div class="page-search" aria-label="Page search">
				<input class="page-search-input" type="search" placeholder="Search..." />
				<button class="page-search-button" type="button">Search</button>
			</div>

			<h1>Search</h1>

			<!-- Projects Section -->
			<section>
				<h2>Dummy Projekte ({{ projects.length }})</h2>
				@if (projects.length === 0) {
					<p>Keine Projekte verfügbar.</p>
				} @else {
					@for (project of projects; track project.id) {
						<a [routerLink]="['/projekte', project.id]" class="project-link">
							<mat-card class="item-card" appearance="outlined">
								<mat-card-header>
									<div class="card-header-content">
										<mat-card-title>{{ project.name }}</mat-card-title>
										<mat-card-subtitle>{{ project.beschreibung }}</mat-card-subtitle>
									</div>
								</mat-card-header>
								<mat-card-content>
									<p><strong>Zeitraum:</strong> {{ project.startdatum | date: "dd.MM.yyyy" }} - {{ project.enddatum | date: "dd.MM.yyyy" }}</p>
									<p><strong>Mitarbeiter:</strong> {{ project.mitarbeiter.length }}</p>
								</mat-card-content>
							</mat-card>
						</a>
					}
				}
			</section>

			<!-- Backend Items Section -->
			<section>
				@let backendItems = data$ | async;

				<h2>Backend Items ({{ backendItems?.total ?? 0 }})</h2>

				@if (!backendItems || (backendItems.items.length === 0)) {
					<p>There are no items available.</p>
				} @else {
					@for (item of backendItems.items; track item.identifier) {
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
	private dummyDataService = inject(DummyDataService);

	data$ = this.http.get<PaginatedPreviewItems>("api/v0/backend/preview-item");
	projects: Project[] = [];
	expandedItem: string | null = null;

	constructor() {
		this.projects = this.dummyDataService.getProjects();
	}

	toggleItem(identifier: string): void {
		this.expandedItem = this.expandedItem === identifier ? null : identifier;
	}
}
