import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'hasKey',
})
export class HasKeyPipe implements PipeTransform {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  transform(value: any, key: any): boolean {
    return key in value;
  }
}
