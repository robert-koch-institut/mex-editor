import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FastTrackResource } from "./fast-track-resource";
import { TestKey, type HarnessLoader } from "@angular/cdk/testing";
import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { MatSelectHarness } from "@angular/material/select/testing";
import { MatSlideToggleHarness } from "@angular/material/slide-toggle/testing";
import { By } from "@angular/platform-browser";
import { TranslocoService } from "@jsverse/transloco";
import { ConceptOptions } from "../../shared/concept-options.service";
import { Fieldset } from "../fieldset/fieldset";
import { MatChipInputHarness } from "@angular/material/chips/testing";
import { MatDatepickerInputHarness } from "@angular/material/datepicker/testing";

const conceptOptionsStub = {
  themeOptions: () => [{ id: "theme-1", label: "Theme 1" }],
  resourceTypeGeneralOptions: () => [{ id: "rtg-1", label: "Type 1" }],
  resourceCreationMethodOptions: () => [{ id: "method-1", label: "Method 1" }],
  frequencyOptions: () => [{ id: "freq-1", label: "Frequency 1" }],
  accessRestrictionOptions: () => [{ id: "ar-1", label: "Restriction 1" }],
};

/** Locates a `mex-fieldset` by its `labelKey` input value. */
function fieldsetEl(fixture: ComponentFixture<FastTrackResource>, fieldname: string) {
  const dataTestId = `fieldset-${fieldname}`;
  const match = fixture.debugElement
    .queryAll(By.directive(Fieldset))
    .find((de) => (de.componentInstance as Fieldset<unknown>).dataTestId === dataTestId);
  if (!match) {
    throw new Error(
      `No mex-fieldset with dataTestId="${dataTestId}" found in the rendered template`,
    );
  }
  return match;
}

function setNativeValue(
  fixture: ComponentFixture<unknown>,
  input: HTMLInputElement | HTMLTextAreaElement,
  value: string,
) {
  input.value = value;
  input.dispatchEvent(new Event("input"));
  input.dispatchEvent(new Event("change"));
  fixture.detectChanges();
}

// eslint-disable-next-line max-lines-per-function
describe("FastTrackResource", () => {
  let fixture: ComponentFixture<FastTrackResource>;
  let component: FastTrackResource;
  let loader: HarnessLoader;

  async function getSelect(vocabName: string) {
    return await loader.getHarness(
      MatSelectHarness.with({ selector: `[data-testid="${vocabName}-select"]` }),
    );
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackResource],
      providers: [{ provide: ConceptOptions, useValue: conceptOptionsStub }],
    }).compileComponents();

    fixture = TestBed.createComponent(FastTrackResource);
    component = fixture.componentInstance;
    loader = TestbedHarnessEnvironment.loader(fixture);
    fixture.detectChanges();
  });

  it("creates the component", () => {
    expect(component).toBeTruthy();
  });

  describe("free-text fields", () => {
    it("captures the title", () => {
      const input = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      setNativeValue(fixture, input, "Sentinel surveillance data");
      expect(component.model().title).toBe("Sentinel surveillance data");
    });

    it("captures the description", () => {
      const textarea = fieldsetEl(fixture, "description").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, textarea, "A resource description");
      expect(component.model().description).toBe("A resource description");
    });

    it("captures the spatial coverage (now wired as a plain string field)", () => {
      const input = fieldsetEl(fixture, "spatial").query(By.css("input")).nativeElement;
      setNativeValue(fixture, input, "Berlin");
      expect(component.model().spatial).toBe("Berlin");
    });

    it("captures the legal basis", () => {
      const textarea = fieldsetEl(fixture, "hasLegalBasis").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, textarea, "Some legal basis");
      expect(component.model().hasLegalBasis).toBe("Some legal basis");
    });

    it("captures the provenance", () => {
      const textarea = fieldsetEl(fixture, "provenance").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, textarea, "Some provenance");
      expect(component.model().provenance).toBe("Some provenance");
    });

    it("captures the rights text", () => {
      const textarea = fieldsetEl(fixture, "rights").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, textarea, "Some rights text");
      expect(component.model().rights).toBe("Some rights text");
    });
  });

  describe("rights prefill toggle", () => {
    it("fills the rights field with the prefill text and disables it when toggled on", async () => {
      const toggle = await loader.getHarness(MatSlideToggleHarness);
      await toggle.check();

      const translocoService = TestBed.inject(TranslocoService);
      expect(component.model().rights).toBe(
        translocoService.translate("fasttrack.resource.fields.rights.prefill.text"),
      );
      expect(component.isPrefillChecked()).toBe(true);
      expect(component.resourceForm.rights().disabled()).toBe(true);
    });

    it("clears the rights field and re-enables it when toggled off again", async () => {
      const toggle = await loader.getHarness(MatSlideToggleHarness);
      await toggle.check();
      await toggle.uncheck();

      expect(component.model().rights).toBe("");
      expect(component.isPrefillChecked()).toBe(false);
      expect(component.resourceForm.rights().disabled()).toBe(false);
    });
  });

  describe("vocabulary multi/single selects", () => {
    it("sets the selected theme(s) in the model", async () => {
      const themeSelect = await getSelect("theme");
      await themeSelect.open();
      await themeSelect.clickOptions({ text: "Theme 1" });
      expect(component.model().theme).toEqual(["theme-1"]);
    });

    it("sets the selected resource type(s) in the model", async () => {
      const resourceTypeSelect = await getSelect("resourceTypeGeneral");
      await resourceTypeSelect.open();
      await resourceTypeSelect.clickOptions({ text: "Type 1" });
      expect(component.model().resourceTypeGeneral).toEqual(["rtg-1"]);
    });

    it("sets the selected resource creation method(s) in the model", async () => {
      const methodSelect = await getSelect("resourceCreationMethod");
      await methodSelect.open();
      await methodSelect.clickOptions({ text: "Method 1" });
      expect(component.model().resourceCreationMethod).toEqual(["method-1"]);
    });

    it("sets the selected accrual periodicity in the model", async () => {
      const frequencySelect = await getSelect("frequency");
      await frequencySelect.open();
      await frequencySelect.clickOptions({ text: "Frequency 1" });
      expect(component.model().accrualPeriodicity).toEqual("freq-1");
    });
  });

  describe("keywords", () => {
    it("adds and removes German keywords via the component methods", () => {
      component.addKeyword("de", "Gesundheit");
      expect(component.model().keywords.de).toEqual(["Gesundheit"]);

      component.addKeyword("de", "Gesundheit"); // duplicates are deduped
      expect(component.model().keywords.de).toEqual(["Gesundheit"]);

      component.removeKeyword("de", "Gesundheit");
      expect(component.model().keywords.de).toEqual([]);
    });

    it("adds and removes English keywords via the component methods", () => {
      component.addKeyword("en", "health");
      expect(component.model().keywords.en).toEqual(["health"]);

      component.removeKeyword("en", "health");
      expect(component.model().keywords.en).toEqual([]);
    });

    it("wires the German keyword input through to the model on Enter", async () => {
      const input = await loader.getHarness(
        MatChipInputHarness.with({
          selector: `mex-fieldset[data-testid="fieldset-de"] input.mat-mdc-chip-input`,
        }),
      );
      await input.setValue("Bevölkerung");
      await input.sendSeparatorKey(TestKey.ENTER);
      await fixture.whenStable();

      expect(component.model().keywords.de).toContain("Bevölkerung");
    });
  });

  describe("date input format depends on the active locale", () => {
    it("parses a German-formatted date ('dd.MM.yyyy') when the locale is 'de'", () => {
      const transloco = TestBed.inject(TranslocoService);
      transloco.setActiveLang("de");

      const input = fieldsetEl(fixture, "start").query(By.css("input"))
        .nativeElement as HTMLInputElement;
      setNativeValue(fixture, input, "27.07.2026");

      expect(component.model().start?.isValid).toBe(true);
      expect(component.model().start?.toISODate()).toBe("2026-07-27");
    });

    it("parses an English-formatted date ('MM/dd/yyyy') when the locale is 'en'", () => {
      const transloco = TestBed.inject(TranslocoService);
      transloco.setActiveLang("en");

      const input = fieldsetEl(fixture, "end").query(By.css("input"))
        .nativeElement as HTMLInputElement;
      setNativeValue(fixture, input, "07/27/2026");

      expect(component.model().end?.isValid).toBe(true);
      expect(component.model().end?.toISODate()).toBe("2026-07-27");
    });

    it("does NOT accept a German-formatted date string while the locale is 'en'", async () => {
      const transloco = TestBed.inject(TranslocoService);
      transloco.setActiveLang("en");

      const input = await loader.getHarness(
        MatDatepickerInputHarness.with({
          selector: "mex-fieldset[data-testid='fieldset-start'] input",
        }),
      );
      await input.setValue("27.07.2026");
      expect(component.model().start).toBe(null);

      await input.setValue("07/27/2026");
      expect(component.model().start?.toISODate()).toBe("2026-07-27");
    });
  });

  describe("fills every wired field and checks the whole model", () => {
    it("ends up with the expected model after filling every field the UI currently supports", async () => {
      const title = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      setNativeValue(fixture, title, "Sentinel surveillance data");

      const description = fieldsetEl(fixture, "description").query(
        By.css("textarea"),
      ).nativeElement;
      setNativeValue(fixture, description, "A resource description");

      component.addContact(); // contacts: [""] -> ["", ""]; content itself needs ContactList

      const [themeSelect, resourceTypeSelect, methodSelect, frequencySelect] = [
        await getSelect("theme"),
        await getSelect("resourceTypeGeneral"),
        await getSelect("resourceCreationMethod"),
        await getSelect("frequency"),
      ];
      await loader.getAllHarnesses(MatSelectHarness);
      await themeSelect.open();
      await themeSelect.clickOptions({ text: "Theme 1" });
      await resourceTypeSelect.open();
      await resourceTypeSelect.clickOptions({ text: "Type 1" });

      const spatial = fieldsetEl(fixture, "spatial").query(By.css("input")).nativeElement;
      setNativeValue(fixture, spatial, "Berlin");

      await methodSelect.open();
      await methodSelect.clickOptions({ text: "Method 1" });
      await frequencySelect.open();
      await frequencySelect.clickOptions({ text: "Frequency 1" });

      TestBed.inject(TranslocoService).setActiveLang("en");
      const start = fieldsetEl(fixture, "start").query(By.css("input"))
        .nativeElement as HTMLInputElement;
      setNativeValue(fixture, start, "01/01/2026");
      const end = fieldsetEl(fixture, "end").query(By.css("input"))
        .nativeElement as HTMLInputElement;
      setNativeValue(fixture, end, "12/31/2026");

      component.addKeyword("de", "Gesundheit");
      component.addKeyword("en", "health");

      const hasLegalBasis = fieldsetEl(fixture, "hasLegalBasis").query(
        By.css("textarea"),
      ).nativeElement;
      setNativeValue(fixture, hasLegalBasis, "Some legal basis");
      const provenance = fieldsetEl(fixture, "provenance").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, provenance, "Some provenance");
      const rights = fieldsetEl(fixture, "rights").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, rights, "Some rights text");

      const model = component.model();
      expect(model.title).toBe("Sentinel surveillance data");
      expect(model.description).toBe("A resource description");
      expect(model.contacts.length).toBe(2);
      expect(model.theme).toEqual(["theme-1"]);
      expect(model.resourceTypeGeneral).toEqual(["rtg-1"]);
      expect(model.spatial).toBe("Berlin");
      expect(model.resourceCreationMethod).toEqual(["method-1"]);
      expect(model.accrualPeriodicity).toBe("freq-1");
      expect(model.start?.toISODate()).toBe("2026-01-01");
      expect(model.end?.toISODate()).toBe("2026-12-31");
      expect(model.keywords).toEqual({ de: ["Gesundheit"], en: ["health"] });
      expect(model.hasLegalBasis).toBe("Some legal basis");
      expect(model.provenance).toBe("Some provenance");
      expect(model.rights).toBe("Some rights text");

      expect(component.resourceForm().valid()).toBe(true);
    });
  });
});
