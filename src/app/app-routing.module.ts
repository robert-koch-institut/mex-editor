import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EntityEditPageComponent } from './pages/entity-edit-page/entity-edit-page.component';
import { EntityNewPageComponent } from './pages/entity-new-page/entity-new-page.component';
import { EntitySearchPageComponent } from './pages/entity-search-page/entity-search-page.component';
import { PageNotFoundPageComponent } from './pages/page-not-found-page/page-not-found-page.component';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { DebugSearchPageComponent } from './pages/debug-search-page/debug-search-page.component';
import { DebugEditPageComponent } from './pages/debug-edit-page/debug-edit-page.component';

const routes: Routes = [
  { path: 'item/new/:entitytype', component: EntityNewPageComponent },
  { path: 'item/:stableTargetId', component: EntityEditPageComponent },

  { path: 'search', redirectTo: 'search/', pathMatch: 'full' },
  { path: 'search/:query', component: EntitySearchPageComponent },

  { path: 'debug/search', component: DebugSearchPageComponent },
  { path: 'debug/edit', component: DebugEditPageComponent },

  { path: '', component: HomePageComponent, pathMatch: 'full' },
  { path: '**', component: PageNotFoundPageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
