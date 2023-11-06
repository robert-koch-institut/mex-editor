import * as _ from 'lodash-es';
import { parseISO, isValid } from 'date-fns';
import { StringFormat } from '../services/formly-field-config-builder.service';

export interface StringFormatMatcher {
  label: string;
  priority: number;
  matches: (value: unknown) => boolean;
}

export const StringFormatMatchers = new Map<StringFormat, StringFormatMatcher>([
  [
    'date',
    {
      label: 'Datum',
      priority: 1,
      matches: (value: unknown) => _.isString(value) && value.indexOf('T') === -1 && isValid(parseISO(value)),
    },
  ],
  [
    'date-time',
    {
      label: 'Datum mit Zeit',
      priority: 10,
      matches: (value: unknown) => _.isString(value) && isValid(parseISO(value)),
    },
  ],
  [
    'datetime',
    {
      label: 'Datum mit Zeit',
      priority: 10,
      matches: (value: unknown) => _.isString(value) && isValid(parseISO(value)),
    },
  ],
  [
    'transient',
    {
      label: 'Text',
      priority: 100,
      matches: (value: unknown) => _.isString(value),
    },
  ],
]);
