import { Pipe, PipeTransform } from '@angular/core';
import * as _ from 'lodash-es';

@Pipe({
  name: 'first',
})
export class FirstPipe implements PipeTransform {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  transform(value: any | any[]): any {
    if (_.isArray(value)) {
      return value.length > 0 ? value[0] : undefined;
    }
    return value;
  }
}
