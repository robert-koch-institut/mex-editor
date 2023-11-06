import { Component } from '@angular/core';
import { EntityType, EntityTypeValues } from 'src/app/models/entity-type';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.scss'],
})
export class HomePageComponent {
  entityTypes = EntityTypeValues;
  selectedEntityType?: EntityType;
  searchQuery = 'a b';
}
