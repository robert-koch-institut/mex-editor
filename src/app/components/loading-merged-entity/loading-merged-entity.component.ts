import { Component, Input, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-loading-merged-entity',
  templateUrl: './loading-merged-entity.component.html',
  styleUrls: ['./loading-merged-entity.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class LoadingMergedEntityComponent {
  @Input() showIcon = true;
  @Input() showTitle = true;
  @Input() showProperties = true;
}
