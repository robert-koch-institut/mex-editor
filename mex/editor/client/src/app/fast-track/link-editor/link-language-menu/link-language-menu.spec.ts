import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import { MatMenuHarness } from "@angular/material/menu/testing";

import { LinkLanguageSchema } from "../../../shared/models/generated/shared";
import { LinkLanguageMenu } from "./link-language-menu";

describe("LinkLanguageMenu", () => {
  let fixture: ComponentFixture<LinkLanguageMenu>;
  const options = Object.values(LinkLanguageSchema.def.entries);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LinkLanguageMenu],
    }).compileComponents();
    fixture = TestBed.createComponent(LinkLanguageMenu);
    fixture.componentRef.setInput("language", options[0]);
    await fixture.whenStable();
  });

  it("shows the current language on the trigger", () => {
    const trigger = fixture.nativeElement.querySelector(".menu-trigger") as HTMLElement;
    expect(trigger.textContent?.trim()).toBe(options[0]);
  });

  it("offers every language option and emits the selected one", async () => {
    const selected: string[] = [];
    fixture.componentInstance.languageSelected.subscribe((l) => selected.push(l));

    const menu = await TestbedHarnessEnvironment.loader(fixture).getHarness(MatMenuHarness);
    await menu.open();
    const items = await menu.getItems();
    expect(items).toHaveLength(options.length);

    await items[options.length - 1].click();
    expect(selected).toEqual([options[options.length - 1]]);
  });

  it("disables the trigger when disabled", async () => {
    fixture.componentRef.setInput("disabled", true);
    const menu = await TestbedHarnessEnvironment.loader(fixture).getHarness(MatMenuHarness);
    expect(await menu.isDisabled()).toBe(true);
  });
});
