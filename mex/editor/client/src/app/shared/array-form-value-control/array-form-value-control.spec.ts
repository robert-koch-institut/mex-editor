import { Component, signal } from "@angular/core";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import { disabled, form, FormField } from "@angular/forms/signals";

import { ArrayFormValueControl, ArrayItemTemplate } from "./array-form-value-control";

@Component({
  imports: [ArrayFormValueControl, ArrayItemTemplate, FormField],
  template: `
    <mex-array-form-value-control
      [formField]="f"
      [createItem]="createItem"
      [minItems]="minItems()"
      [maxItems]="maxItems()"
      [reorderable]="reorderable()"
    >
      <ng-template [mexArrayItem]="f" let-field="field">
        <input [formField]="field" />
      </ng-template>
    </mex-array-form-value-control>
  `,
})
class HostComponent {
  readonly model = signal<string[]>(["a", "b", "c"]);
  readonly isDisabled = signal(false);
  readonly minItems = signal(0);
  readonly maxItems = signal<number | undefined>(undefined);
  readonly reorderable = signal(true);
  readonly f = form(this.model, (p) => disabled(p, { when: () => this.isDisabled() }));
  createItem = () => "new";
}

describe("ArrayFormValueControl", () => {
  let fixture: ComponentFixture<HostComponent>;
  let host: HostComponent;
  let el: HTMLElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [HostComponent] }).compileComponents();
    fixture = TestBed.createComponent(HostComponent);
    host = fixture.componentInstance;
    el = fixture.nativeElement;
    await fixture.whenStable();
  });

  const rows = () => Array.from(el.querySelectorAll<HTMLElement>("li.row"));
  const inputs = () => Array.from(el.querySelectorAll<HTMLInputElement>("li.row input"));
  const values = () => inputs().map((i) => i.value);
  const button = (icon: string, row?: number): HTMLButtonElement => {
    const scope = row === undefined ? el : rows()[row];
    const found = Array.from(scope.querySelectorAll("button")).find(
      (b) => b.querySelector("mat-icon")?.textContent?.trim() === icon,
    );
    if (!found) throw new Error(`button "${icon}" not found`);
    return found;
  };
  const click = async (b: HTMLButtonElement) => {
    b.click();
    await fixture.whenStable();
  };

  it("renders one row per item", () => {
    expect(values()).toEqual(["a", "b", "c"]);
  });

  it("adds an item created by createItem", async () => {
    await click(button("add"));
    expect(host.model()).toEqual(["a", "b", "c", "new"]);
    expect(rows()).toHaveLength(4);
  });

  it("disables add when maxItems is reached", async () => {
    host.maxItems.set(3);
    await fixture.whenStable();
    expect(button("add").disabled).toBe(true);
  });

  it("removes the clicked item", async () => {
    await click(button("close", 1));
    expect(host.model()).toEqual(["a", "c"]);
  });

  it("disables remove when minItems is reached", async () => {
    host.minItems.set(3);
    await fixture.whenStable();
    expect(button("close", 0).disabled).toBe(true);
  });

  it("moves items up and down", async () => {
    await click(button("arrow_downward", 0));
    expect(host.model()).toEqual(["b", "a", "c"]);
    await click(button("arrow_upward", 2));
    expect(host.model()).toEqual(["b", "c", "a"]);
  });

  it("disables move up on the first and move down on the last row", () => {
    expect(button("arrow_upward", 0).disabled).toBe(true);
    expect(button("arrow_downward", 2).disabled).toBe(true);
  });

  it("hides move buttons when not reorderable", async () => {
    host.reorderable.set(false);
    await fixture.whenStable();
    expect(el.textContent).not.toContain("arrow_upward");
    expect(el.textContent).not.toContain("arrow_downward");
  });

  it("disables all buttons when the form is disabled", async () => {
    host.isDisabled.set(true);
    await fixture.whenStable();
    expect(Array.from(el.querySelectorAll("button")).every((b) => b.disabled)).toBe(true);
  });

  it("keeps the DOM node of remaining rows when another row is removed", async () => {
    const secondInput = inputs()[1];
    await click(button("close", 0));
    expect(inputs()[0]).toBe(secondInput);
  });
});
