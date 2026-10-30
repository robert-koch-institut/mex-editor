import { NgTemplateOutlet } from "@angular/common";
import {
  Component,
  computed,
  contentChild,
  Directive,
  inject,
  input,
  linkedSignal,
  model,
  output,
  TemplateRef,
} from "@angular/core";
import type { FieldTree, ValidationError, WithOptionalFieldTree } from "@angular/forms/signals";
import { FORM_FIELD, FormField, type FormValueControl } from "@angular/forms/signals";

/**
 * ArrayItemContext API documentation.
 */
export interface ArrayItemContext<T> {
  $implicit: FieldTree<T>;
  field: FieldTree<T>;
  value: T;
  index: number;
  first: boolean;
  last: boolean;
}

@Directive({ selector: "ng-template[mexArrayItem]" })
/**
 * ArrayItemTemplate API documentation.
 */
export class ArrayItemTemplate<T> {
  /** Only a type hint for the template type checker. Pass the same field as on the host. */
  readonly mexArrayItem = input<FieldTree<T[]> | undefined>();
  readonly template = inject<TemplateRef<ArrayItemContext<T>>>(TemplateRef);

  static ngTemplateContextGuard<T>(
    _dir: ArrayItemTemplate<T>,
    _ctx: unknown,
  ): _ctx is ArrayItemContext<T> {
    return true;
  }
}

@Component({
  selector: "mex-array-form-value-control",
  imports: [NgTemplateOutlet],
  templateUrl: "./array-form-value-control.html",
  styleUrl: "./array-form-value-control.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
/**
 * Generic control to add and remove items from an array.
 */
export class ArrayFormValueControl<T> implements FormValueControl<T[]> {
  readonly value = model<T[]>([]);
  // --- Configuration ---
  readonly createItem = input.required<() => T>();
  readonly minItems = input(0);
  readonly maxItems = input<number | undefined>(undefined);
  readonly reorderable = input(true);
  readonly addLabel = input("Add");
  readonly removeLabel = input("Remove");
  readonly moveUpLabel = input("Move up");
  readonly moveDownLabel = input("Move down");

  // --- Optional form state (filled by [formField]) ---
  readonly disabled = input(false);
  readonly readonly = input(false);
  readonly hidden = input(false);
  readonly invalid = input(false);
  readonly errors = input<readonly WithOptionalFieldTree<ValidationError>[]>([]);
  readonly touch = output<void>();

  protected readonly itemTemplate = contentChild.required<ArrayItemTemplate<T>>(ArrayItemTemplate);

  // Throws NG0201 if used without [formField]. That is intended.
  private readonly formField = inject(FORM_FIELD);
  private readonly tree = computed(() => this.formField.field() as unknown as FieldTree<T[]>);

  // --- Stable row ids (so views and focus survive remove/move) ---
  private nextId = 0;
  private readonly ids = linkedSignal<number, number[]>({
    source: () => this.value().length,
    computation: (len, prev) => {
      const ids = prev?.value ?? [];
      if (ids.length === len) return ids;
      if (ids.length > len) return ids.slice(0, len);
      return [...ids, ...Array.from({ length: len - ids.length }, () => this.nextId++)];
    },
  });

  protected readonly rows = computed(() => {
    const items = this.value();
    const tree = this.tree();
    const ids = this.ids();
    return ids.map((id, index) => {
      const field = tree[index] as unknown as FieldTree<T>;
      const context: ArrayItemContext<T> = {
        $implicit: field,
        field,
        value: items[index] as T,
        index,
        first: index === 0,
        last: index === ids.length - 1,
      };
      return { id, context };
    });
  });

  protected readonly editable = computed(() => !this.disabled() && !this.readonly());
  protected readonly canAdd = computed(() => {
    const max = this.maxItems();
    return this.editable() && (max === undefined || this.value().length < max);
  });
  protected readonly canRemove = computed(
    () => this.editable() && this.value().length > this.minItems(),
  );

  protected add(): void {
    if (!this.canAdd()) return;
    const item = this.createItem()();
    this.ids.update((ids) => [...ids, this.nextId++]);
    this.value.update((arr) => [...arr, item]);
    this.touch.emit();
  }

  protected remove(index: number): void {
    if (!this.canRemove()) return;
    this.ids.update((ids) => ids.filter((_, i) => i !== index));
    this.value.update((arr) => arr.filter((_, i) => i !== index));
    this.touch.emit();
  }

  protected move(index: number, delta: -1 | 1): void {
    const target = index + delta;
    if (!this.editable() || target < 0 || target >= this.value().length) return;
    this.ids.update((ids) => swap(ids, index, target));
    this.value.update((arr) => swap(arr, index, target));
    this.touch.emit();
  }
}

function swap<U>(arr: readonly U[], a: number, b: number): U[] {
  const next = [...arr];
  [next[a], next[b]] = [next[b], next[a]];
  return next;
}
