export function logMore<T>(when: 'in' | 'out' | 'inout', more: (that: T, args: unknown[]) => unknown) {
  return function (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const className = target.constructor.name;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    descriptor.value = function (...args: any[]) {
      if (when === 'in' || when === 'inout') {
        console.log(`${className} :: ${propertyKey}(`, ...args, ')', ' + ', more(this as T, args));
      }
      const result = originalMethod.apply(this, args);
      if (when === 'out' || when === 'inout') {
        console.log(`${className} :: ${propertyKey}(`, ...args, '): ', result, ' + ', more(this as T, args));
      }
      return result;
    };

    return descriptor;
  };
}

export function log(when: 'in' | 'out' | 'inout') {
  return function (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const className = target.constructor.name;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    descriptor.value = function (...args: any[]) {
      if (when === 'in' || when === 'inout') {
        console.log(`${className} :: ${propertyKey}(`, ...args, ')');
      }
      const result = originalMethod.apply(this, args);
      if (when === 'out' || when === 'inout') {
        console.log(`${className} :: ${propertyKey}(`, ...args, '): ', result);
      }
      return result;
    };

    return descriptor;
  };
}
