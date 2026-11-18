import type { HarnessLoader } from "@angular/cdk/testing";
import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { MatIconTestingModule } from "@angular/material/icon/testing";
import { MatMenuHarness } from "@angular/material/menu/testing";
import type { TranslateParams } from "@jsverse/transloco";
import { TranslocoService } from "@jsverse/transloco";
import { vi } from "vitest";

import type { DatepickerPrecision } from "./precision";
import { PrecisionMenu } from "./precision-menu";

describe("PrecisionMenu", () => {
  let fixture: ComponentFixture<PrecisionMenu>;
  let loader: HarnessLoader;

  function setup(inputs: {
    precision?: DatepickerPrecision;
    options?: DatepickerPrecision[];
    disabled?: boolean;
  }) {
    const values = { precision: "day", options: ["year", "month", "day"], ...inputs };
    for (const [name, value] of Object.entries(values)) {
      fixture.componentRef.setInput(name, value);
    }
    fixture.detectChanges();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PrecisionMenu, MatIconTestingModule],
    }).compileComponents();

    vi.spyOn(TestBed.inject(TranslocoService), "translate").mockImplementation(
      (key: TranslateParams) => key as string,
    );

    fixture = TestBed.createComponent(PrecisionMenu);
    loader = TestbedHarnessEnvironment.loader(fixture);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("offers exactly the given options", async () => {
    setup({ options: ["year", "month"] });
    const menu = await loader.getHarness(MatMenuHarness);

    await menu.open();
    const items = await menu.getItems();

    expect(await Promise.all(items.map((item) => item.getText()))).toStrictEqual([
      "datepicker.precision.year",
      "datepicker.precision.month",
    ]);
  });

  it("emits the chosen precision", async () => {
    const selected = vi.fn();
    setup({});
    fixture.componentInstance.precisionSelected.subscribe(selected);
    const menu = await loader.getHarness(MatMenuHarness);

    await menu.clickItem({ text: "datepicker.precision.month" });

    expect(selected).toHaveBeenCalledExactlyOnceWith("month");
  });

  it("is not opened when disabled", async () => {
    setup({ disabled: true });
    const menu = await loader.getHarness(MatMenuHarness);

    expect(await menu.isDisabled()).toBe(true);
  });
});
