import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { random } from 'lodash-es';
import { nameOf } from 'src/app/util/name-of';

@Component({
  selector: 'app-loading-label-fake',
  templateUrl: './loading-label-fake.component.html',
  styleUrls: ['./loading-label-fake.component.scss'],
})
export class LoadingLabelFakeComponent implements OnChanges {
  @Input() clazz = '';
  @Input() minWords = 1;
  @Input() maxWords = 5;
  @Input() maxWidth = 100;

  words: string[] = [];

  constructor() {
    this._updateWords();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (
      nameOf<LoadingLabelFakeComponent>('minWords') in changes ||
      nameOf<LoadingLabelFakeComponent>('maxWords') in changes ||
      nameOf<LoadingLabelFakeComponent>('maxWidth') in changes
    ) {
      this._updateWords();
    }
  }

  private _updateWords() {
    const wordCount = random(this.minWords, this.maxWords);
    const words = [];
    let availableWidth = this.maxWidth;

    for (let i = 0; i < wordCount; i++) {
      const width = random(1, availableWidth === this.maxWidth ? this.maxWidth * 0.3 : availableWidth);
      availableWidth -= width;
      words.push(`${width}%`);
    }
    this.words = words;
  }
}
