import type { Signal } from "@angular/core";

/**
 * LabeledControl API documentation.
 */
export abstract class LabeledControl {
  readonly labels: Record<string, () => string | Signal<string>> = {};
}
