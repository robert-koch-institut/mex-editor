import { inject, InjectionToken } from '@angular/core';
import { ConfigOption, FORMLY_CONFIG } from '@ngx-formly/core';
import { TypeOption } from '@ngx-formly/core/lib/models';
import * as _ from 'lodash-es';

function addWrapperRecursive(typeOpt: TypeOption, map: Map<string, string[]>, typeOpts: TypeOption[]) {
  if (typeOpt.wrappers) {
    if (map.has(typeOpt.name)) {
      // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
      map.set(typeOpt.name, [...map.get(typeOpt.name)!, ...typeOpt.wrappers]);
    } else {
      map.set(typeOpt.name, typeOpt.wrappers);
    }
  } else if (typeOpt.extends) {
    const extendedType = typeOpts.find((x) => x.name === typeOpt.extends);
    addWrapperRecursive({ ...extendedType, ...typeOpt }, map, typeOpts);
  }
}

export function createFormlyWrapperMap(formlyConfig: ConfigOption[] = inject(FORMLY_CONFIG)): Map<string, string[]> {
  const wrapperMap = new Map<string, string[]>();
  const types = _.flatMap(formlyConfig, (x) => x.types ?? []);
  types.forEach((t) => {
    addWrapperRecursive(t, wrapperMap, types);
  });
  return wrapperMap;
}

export const FORMLY_WRAPPER_MAP = new InjectionToken<Map<string, string[]>>('FORMLY-WRAPPER-MAP');
