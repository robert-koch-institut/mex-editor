import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { type ComponentFixture, TestBed } from "@angular/core/testing";
import { MatMenuHarness } from "@angular/material/menu/testing";

import { TextLanguageSchema } from "../../models/generated/shared";
import { TextLanguageMenu } from "./text-language-menu";

describe("TextLanguageMenu", () => {
  let fixture: ComponentFixture<TextLanguageMenu>;
  const options = Object.values(TextLanguageSchema.def.entries);

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextLanguageMenu],
    }).compileComponents();
    fixture = TestBed.createComponent(TextLanguageMenu<false>);
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

describe("TextLanguageMenu as nullable", () => {
  let fixture: ComponentFixture<TextLanguageMenu<true>>;
  const options = [...Object.values(TextLanguageSchema.def.entries), null];

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextLanguageMenu],
    }).compileComponents();
    fixture = TestBed.createComponent(TextLanguageMenu<true>);
    fixture.componentRef.setInput("language", null);
    fixture.componentRef.setInput("nullable", true);
    await fixture.whenStable();
  });

  it("shows the current language on the trigger", () => {
    const trigger = fixture.nativeElement.querySelector(".menu-trigger") as HTMLElement;
    expect(trigger.textContent?.trim()).toBe("-");
  });

  it("offers every language option and emits the selected one", async () => {
    const selected: (string | null)[] = [];
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
