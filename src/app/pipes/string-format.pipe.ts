import { DatePipe } from '@angular/common';
import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash-es';
import { StringFormatMatchers } from '../models/string-format-matcher';
import { StringFormat } from '../services/formly-field-config-builder.service';

@Pipe({
  name: 'stringFormat',
})
export class StringFormatPipe implements PipeTransform {
  private readonly _datePipe = new DatePipe('de');

  transform(value: string, format: StringFormat | StringFormat[] = 'transient'): string | null {
    if (_.isArray(format)) {
      const found = _.find(
        format,
        (f) =>
          StringFormatMatchers.has(f) &&
          // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
          StringFormatMatchers.get(f)!.matches(value)
      );
      format = found !== undefined ? found : 'transient';
    }

    switch (format) {
      case 'date':
        return this._datePipe.transform(value, 'mediumDate');
      case 'date-time':
      case 'datetime':
        return this._datePipe.transform(value, 'medium');
      case 'transient':
      default:
        return value;
    }
  }
}
