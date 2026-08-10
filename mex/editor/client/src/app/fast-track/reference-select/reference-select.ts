import {
  Component,
  computed,
  debounced,
  inject,
  input,
  model,
  output,
  signal,
} from "@angular/core";
import { httpResource } from "@angular/common/http";
import { MatFormField, MatLabel, MatOptgroup, MatOption } from "@angular/material/select";
import { MatIcon, MatIconModule } from "@angular/material/icon";
import type { PaginatedItemsContainer } from "../../shared/models/paginated-items-container";
import type { MatAutocompleteTrigger } from "@angular/material/autocomplete";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { MatInput, MatInputModule } from "@angular/material/input";
import { TypeToIconNamePipe } from "../../shared/type-to-icon-name-pipe";
import { FormField, type FormValueControl } from "@angular/forms/signals";
import { MatCheckbox } from "@angular/material/checkbox";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatButtonModule } from "@angular/material/button";
import { MatChipsModule } from "@angular/material/chips";
import { FormsModule } from "@angular/forms";
import {
  translateObjectSignal,
  TranslocoDirective,
  TranslocoPipe,
  TranslocoService,
} from "@jsverse/transloco";
import { translateSignal } from "@jsverse/transloco";
import { combineLatest, map, switchMap } from "rxjs";
import { toObservable, toSignal } from "@angular/core/rxjs-interop";
import { MatDialog } from "@angular/material/dialog";
import type {
  CreateItemDialogData,
  CreateItemDialogResult,
} from "../create-item-dialog/create-item-dialog";
import { CreateItemDialog } from "../create-item-dialog/create-item-dialog";
import { ToLabelPipe } from "../../shared/to-label-pipe";
import type { PreviewItem } from "../../shared/models";
import type { CreateItem } from "../../shared/models/create-item";
import { isCreateItem } from "../../shared/models/create-item";

/**
 * Type for valid reference select types.
 */
export type ReferenceSelectTypes = "Person" | "ContactPoint" | "OrganizationalUnit";

@Component({
  selector: "mex-reference-select",
  imports: [
    MatIcon,
    MatOption,
    MatOptgroup,
    MatCheckbox,
    TypeToIconNamePipe,
    MatFormField,
    MatLabel,
    MatIconModule,
    MatAutocompleteModule,
    MatInput,
    FormsModule,
    MatChipsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    ToLabelPipe,
    TranslocoDirective,
    TranslocoPipe,
  ],
  templateUrl: "./reference-select.html",
  styleUrl: "./reference-select.scss",
  hostDirectives: [{ directive: FormField, inputs: ["formField"] }],
})
/**
 * Component to search and/or create a reference entity.
 */
export class ReferenceSelect<
  T extends PreviewItem | CreateItem = PreviewItem | CreateItem,
> implements FormValueControl<T[]> {
  protected readonly transloco = inject(TranslocoService);
  private readonly labelPipe = new ToLabelPipe();
  private readonly dialog = inject(MatDialog);

  readonly validEntityTypes = input<ReferenceSelectTypes[]>([
    "Person",
    "ContactPoint",
    "OrganizationalUnit",
  ]);
  readonly value = model<T[]>([]);
  isCreationEnabled = input(false);
  readonly touch = output<void>();

  protected readonly isInputFocused = signal(false);

  protected readonly searchQuery = signal("");
  protected readonly searchEntityTypes = signal(this.validEntityTypes());

  protected readonly labelPlaceholderParam = computed(() => ({
    value: this.validEntityTypeLabels(),
  }));
  protected readonly labelPlaceholder = translateObjectSignal(
    "reference-select.placeholder.validTypes",
    this.labelPlaceholderParam,
  );
  protected readonly label = computed(() => {
    const isFocused = this.isInputFocused();
    const val = this.value();
    const lang = this.transloco.activeLang();
    if (!isFocused && val.length > 0) {
      return val.map((x) => this.labelPipe.transform(x, lang)).join(", ");
    }
    return this.labelPlaceholder();
  });
  protected readonly emptyPlaceholderLabel = translateSignal("reference-select.placeholder.empty");

  protected readonly searchQueryDebounced = debounced(() => this.searchQuery(), 200);
  protected readonly searchResult = httpResource<PaginatedItemsContainer<PreviewItem>>(() => {
    const params = {
      q: this.searchQueryDebounced.value().trim(),
      entityType: this.searchEntityTypes().map((x) => `Merged${x}`),
    };
    if (!params.q || params.entityType.length === 0) {
      return undefined;
    }

    return {
      url: "/api/v0/backend/preview-item",
      params,
    };
  });

  protected readonly validEntityTypeLabels = toSignal(
    toObservable(this.validEntityTypes).pipe(
      switchMap((x) => combineLatest(x.map((item) => this.transloco.selectTranslate(item)))),
      map((x) => x.join(", ")),
    ),
  );

  private uniqueById(items: T[]): T[] {
    return [
      ...new Map(items.map((item, i) => [isCreateItem(item) ? i : item.identifier, item])).values(),
    ];
  }

  protected displayFn(entity: PreviewItem | string | null): string {
    if (!entity) return "";
    if (typeof entity === "string") return entity;

    return entity.identifier;
  }

  protected showCreateDialog() {
    const dialogRef = this.dialog.open<
      CreateItemDialog,
      CreateItemDialogData,
      CreateItemDialogResult
    >(CreateItemDialog, {
      data: {
        inputText: this.searchQuery(),
        allowedTypes: this.validEntityTypes() as CreateItemDialogData["allowedTypes"],
      },
      autoFocus: ".focus-me",
      restoreFocus: true,
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.addValue(result as T);
      }
    });
  }

  protected openPanelDelayed(trigger: MatAutocompleteTrigger) {
    setTimeout(() => trigger.openPanel(), 10);
  }

  protected toggleSearchEntityType(entityType: ReferenceSelectTypes) {
    const values = this.searchEntityTypes();
    const update = values.includes(entityType)
      ? values.filter((x) => x !== entityType)
      : [...values, entityType];

    this.searchEntityTypes.set(update);
  }

  protected removeValue(item: T) {
    const update = isCreateItem(item)
      ? this.value().filter((x) => x !== item)
      : this.value().filter((x) => (isCreateItem(x) ? true : x.identifier !== item.identifier));
    this.value.set(update);
  }

  protected addValue(item: T) {
    if (item) {
      const update = this.uniqueById([...this.value(), item]);
      this.value.set(update);
      this.searchQuery.set("");
    }
  }
}
