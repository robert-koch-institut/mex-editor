import { type HarnessLoader } from "@angular/cdk/testing";
import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { MatDatepickerInputHarness } from "@angular/material/datepicker/testing";
import { MatSelectHarness } from "@angular/material/select/testing";
import { By } from "@angular/platform-browser";
import { Router } from "@angular/router";
import { TranslocoService } from "@jsverse/transloco";

import { ConceptLookups } from "../../shared/concept-lookups.service";
import type { PreviewItem } from "../../shared/models";
import { asLinkLanguage } from "../../shared/models";
import type { CreateItem } from "../../shared/models/create-item";
import { ActivityTypeSchema } from "../../shared/models/generated/activity";
import { SubmissionError } from "../../shared/models/submission-result";
import { ToastNotifier } from "../../shared/toasts/toast-notifier";
import { FastTrackSubmission } from "../fast-track-submission";
import { Fieldset } from "../fieldset/fieldset";
import { ReferenceSelect } from "../reference-select/reference-select";
import { FastTrackActivity } from "./fast-track-activity";

const ACTIVITY_TYPE_ID = ActivityTypeSchema.enum["https://mex.rki.de/item/activity-type-1"];

const conceptOptionsStub = {
  activityTypeOptions: () => [{ id: ACTIVITY_TYPE_ID, label: "Type 1" }],
};

function createId(identifier: string): string {
  return identifier.replace("-", "").padStart(21, "a");
}

const VALID_PERSON = (identifier: string, fullName: string) => ({
  $type: "PreviewPerson" as const,
  identifier: createId(identifier),
  fullName: [fullName],
});
const VALID_CONTACT_POINT = (identifier: string, email: string) => ({
  $type: "PreviewContactPoint" as const,
  identifier: createId(identifier),
  email: [email],
});
const VALID_ORG_UNIT = (identifier: string, shortName: string) => ({
  $type: "PreviewOrganizationalUnit" as const,
  identifier: createId(identifier),
  shortName: [{ value: shortName }],
});
// ASSUMPTION: shape of PreviewOrganization (officialName as Text[]).
const VALID_ORGANIZATION = (identifier: string, officialName: string) => ({
  $type: "PreviewOrganization" as const,
  identifier: createId(identifier),
  officialName: [{ value: officialName }],
});

/**
 * Locates a `mex-fieldset` by its static `labelKey` attribute. The activity template sets no
 * `dataTestId`, so the labelKey (unique per fieldset) is used instead.
 */
function fieldsetEl(fixture: ComponentFixture<FastTrackActivity>, labelKey: string) {
  const match = fixture.debugElement
    .queryAll(By.directive(Fieldset))
    .find((de) => (de.nativeElement as HTMLElement).getAttribute("labelKey") === labelKey);
  if (!match) {
    throw new Error(`No mex-fieldset with labelKey="${labelKey}" found in the rendered template`);
  }
  return match;
}

/** Locates the `mex-reference-select` instance inside a given fieldset. */
function referenceSelectIn<T extends PreviewItem | CreateItem>(
  fixture: ComponentFixture<FastTrackActivity>,
  labelKey: string,
) {
  const match = fieldsetEl(fixture, labelKey).query(By.directive(ReferenceSelect<T>));
  if (!match) {
    throw new Error(`No mex-reference-select found inside the "${labelKey}" fieldset`);
  }
  return match.componentInstance as ReferenceSelect<T>;
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

async function datepickerInputs(loader: HarnessLoader) {
  const [start, end] = await loader.getAllHarnesses(MatDatepickerInputHarness);
  return { start, end };
}

/** Finds an icon button (e.g. "add", "close", "arrow_upward") inside the array control. */
function iconButton(scope: HTMLElement, icon: string, row?: number): HTMLButtonElement {
  const root = row === undefined ? scope : scope.querySelectorAll<HTMLElement>("li.row")[row];
  const found = Array.from(root.querySelectorAll("button")).find(
    (b) => b.querySelector("mat-icon")?.textContent?.trim() === icon,
  );
  if (!found) throw new Error(`button "${icon}" not found`);
  return found;
}

// eslint-disable-next-line max-lines-per-function
describe("FastTrackActivity", () => {
  let fixture: ComponentFixture<FastTrackActivity>;
  let component: FastTrackActivity;
  let loader: HarnessLoader;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FastTrackActivity],
      providers: [
        { provide: ConceptLookups, useValue: conceptOptionsStub },
        { provide: FastTrackSubmission, useValue: { submit: vi.fn() } },
        {
          provide: ToastNotifier,
          useValue: { success: vi.fn(), error: vi.fn(), submissionError: vi.fn() },
        },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(FastTrackActivity);
    component = fixture.componentInstance;
    loader = TestbedHarnessEnvironment.loader(fixture);
    fixture.detectChanges();
    await fixture.whenStable();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  function fillEveryRequiredField() {
    const title = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
    setNativeValue(fixture, title, "A valid title");
    const abstract = fieldsetEl(fixture, "abstract").query(By.css("textarea")).nativeElement;
    setNativeValue(fixture, abstract, "A valid abstract");
    referenceSelectIn(fixture, "contact").value.set([VALID_CONTACT_POINT("contact-1", "a@b.com")]);
    referenceSelectIn(fixture, "Activity.responsibleUnit").value.set([
      VALID_ORG_UNIT("unit-1", "RKI"),
    ]);
    component.model.update((m) => ({
      ...m,
      activityType: [ACTIVITY_TYPE_ID],
    }));
    fixture.detectChanges();
  }

  const submitForm = async () => {
    const form = fixture.nativeElement.querySelector("form") as HTMLFormElement;
    expect(form).toBeTruthy();
    form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    await fixture.whenStable();
  };

  it("creates the component", () => {
    expect(component).toBeTruthy();
  });

  it("renders the translated page headline", () => {
    const headline = fixture.nativeElement.querySelector("h1.page-title") as HTMLElement;
    expect(headline.textContent?.trim()).toBe(
      TestBed.inject(TranslocoService).translate("fasttrack.activity.headline"),
    );
  });

  describe("free-text fields", () => {
    it("captures the title", () => {
      const input = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      setNativeValue(fixture, input, "Sentinel surveillance project");
      expect(component.model().title).toBe("Sentinel surveillance project");
    });

    it("captures the short name", () => {
      const input = fieldsetEl(fixture, "shortName").query(By.css("input")).nativeElement;
      setNativeValue(fixture, input, "SSP");
      expect(component.model().shortName).toBe("SSP");
    });

    it("captures the abstract (fieldset labelled 'abstract')", () => {
      const textarea = fieldsetEl(fixture, "abstract").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, textarea, "An activity abstract");
      expect(component.model().abstract).toBe("An activity abstract");
    });
  });

  describe("activity type select", () => {
    it("sets the selected activity type(s) in the model", async () => {
      const select = await loader.getHarness(
        MatSelectHarness.with({ selector: `[data-testid="activityType-select"]` }),
      );
      await select.open();
      await select.clickOptions({ text: "Type 1" });
      expect(component.model().activityType).toEqual([ACTIVITY_TYPE_ID]);
    });
  });

  describe("date input format depends on the active locale", () => {
    // ASSUMPTION: the datepicker writes ISO strings ("2026-07-27") into the model.
    it("parses a German-formatted date ('DD.MM.yyyy') when the language is 'de'", async () => {
      TestBed.inject(TranslocoService).setActiveLang("de");
      fixture.detectChanges();

      const { start } = await datepickerInputs(loader);
      await start.setValue("27.07.2026");

      expect(component.model().start?.toISODate()).toBe("2026-07-27");
    });

    it("parses an English-formatted date ('MM/DD/yyyy') when the language is 'en'", async () => {
      TestBed.inject(TranslocoService).setActiveLang("en");
      fixture.detectChanges();

      const { end } = await datepickerInputs(loader);
      await end.setValue("07/27/2026");

      expect(component.model().end?.toISODate()).toBe("2026-07-27");
    });

    it("does NOT accept a German-formatted date string while the language is 'en'", async () => {
      TestBed.inject(TranslocoService).setActiveLang("en");
      fixture.detectChanges();

      const { start } = await datepickerInputs(loader);
      await start.setValue("27.07.2026"); // not a valid en short date

      expect(component.model().start).toBe(null);
    });
  });

  describe("reference fields (contact, involvedPerson, responsibleUnit, involvedUnit, funderOrCommissioner)", () => {
    it("captures selected contacts", () => {
      const contact = VALID_CONTACT_POINT("contact-1", "info@example.org");
      referenceSelectIn(fixture, "contact").value.set([contact]);
      fixture.detectChanges();
      expect(component.model().contact).toEqual([contact]);
    });

    it("captures selected involved persons", () => {
      const person = VALID_PERSON("person-1", "Jane Doe");
      referenceSelectIn(fixture, "Activity.involvedPerson").value.set([person]);
      fixture.detectChanges();
      expect(component.model().involvedPerson).toEqual([person]);
    });

    it("captures the selected responsible unit", () => {
      const unit = VALID_ORG_UNIT("unit-1", "RKI");
      referenceSelectIn(fixture, "Activity.responsibleUnit").value.set([unit]);
      fixture.detectChanges();
      expect(component.model().responsibleUnit).toEqual([unit]);
    });

    it("captures the selected involved unit", () => {
      const unit = VALID_ORG_UNIT("unit-2", "Dept X");
      referenceSelectIn(fixture, "Activity.involvedUnit").value.set([unit]);
      fixture.detectChanges();
      expect(component.model().involvedUnit).toEqual([unit]);
    });

    it("captures the selected funder or commissioner", () => {
      const org = VALID_ORGANIZATION("org-1", "Funding Org");
      referenceSelectIn(fixture, "Activity.funderOrCommissioner").value.set([org]);
      fixture.detectChanges();
      expect(component.model().funderOrCommissioner).toEqual([org]);
    });

    it("restricts the selectable entity types per field", () => {
      expect(referenceSelectIn(fixture, "contact").validEntityTypes()).toEqual([
        "ContactPoint",
        "Person",
        "OrganizationalUnit",
      ]);
      expect(referenceSelectIn(fixture, "Activity.involvedPerson").validEntityTypes()).toEqual([
        "Person",
      ]);
      expect(referenceSelectIn(fixture, "Activity.responsibleUnit").validEntityTypes()).toEqual([
        "OrganizationalUnit",
      ]);
      expect(referenceSelectIn(fixture, "Activity.involvedUnit").validEntityTypes()).toEqual([
        "OrganizationalUnit",
      ]);
      expect(
        referenceSelectIn(fixture, "Activity.funderOrCommissioner").validEntityTypes(),
      ).toEqual(["Organization"]);
    });

    it("enables item creation for contact/involvedPerson/funderOrCommissioner but not the unit fields", () => {
      expect(referenceSelectIn(fixture, "contact").isCreationEnabled()).toBe(true);
      expect(referenceSelectIn(fixture, "Activity.involvedPerson").isCreationEnabled()).toBe(true);
      expect(referenceSelectIn(fixture, "Activity.funderOrCommissioner").isCreationEnabled()).toBe(
        true,
      );
      expect(referenceSelectIn(fixture, "Activity.responsibleUnit").isCreationEnabled()).toBe(
        false,
      );
      expect(referenceSelectIn(fixture, "Activity.involvedUnit").isCreationEnabled()).toBe(false);
    });

    it("accepts a ContactPoint as a contact", () => {
      referenceSelectIn(fixture, "contact").value.set([
        VALID_CONTACT_POINT("contact-2", "team@example.org"),
      ]);
      fixture.detectChanges();
      expect(component.activityForm.contact().errors()).toEqual([]);
    });

    it("accepts a Person as a contact", () => {
      referenceSelectIn(fixture, "contact").value.set([VALID_PERSON("person-3", "Contact Person")]);
      fixture.detectChanges();
      expect(component.activityForm.contact().errors()).toEqual([]);
    });

    it("accepts an OrganizationalUnit as a contact", () => {
      referenceSelectIn(fixture, "contact").value.set([VALID_ORG_UNIT("unit-3", "Some Dept")]);
      fixture.detectChanges();
      expect(component.activityForm.contact().errors()).toEqual([]);
    });
  });

  describe("website links (array control + link editor)", () => {
    const websiteEl = () => fieldsetEl(fixture, "website").nativeElement as HTMLElement;
    const urlInputs = () =>
      Array.from(websiteEl().querySelectorAll<HTMLInputElement>("li.row input[type=url]"));
    const click = async (button: HTMLButtonElement) => {
      button.click();
      await fixture.whenStable();
    };

    it("adds a link with an empty url and the active language", async () => {
      await click(iconButton(websiteEl(), "add"));

      const activeLang = TestBed.inject(TranslocoService).getActiveLang();
      expect(component.model().website).toMatchObject([
        { url: "", language: asLinkLanguage(activeLang) },
      ]);
      expect(urlInputs()).toHaveLength(1);
    });

    it("captures the url typed into a link editor", async () => {
      await click(iconButton(websiteEl(), "add"));
      setNativeValue(fixture, urlInputs()[0], "https://example.org");
      await fixture.whenStable();
      expect(component.model().website[0].url).toBe("https://example.org");
    });

    it("removes a link", async () => {
      await click(iconButton(websiteEl(), "add"));
      await click(iconButton(websiteEl(), "add"));
      expect(component.model().website).toHaveLength(2);

      await click(iconButton(websiteEl(), "close", 0));
      expect(component.model().website).toHaveLength(1);
    });

    it("is invalid while a link has an empty url and valid once the url is set", async () => {
      fillEveryRequiredField();
      expect(component.activityForm().valid()).toBe(true);

      await click(iconButton(websiteEl(), "add"));
      expect(component.activityForm().valid()).toBe(false);

      setNativeValue(fixture, urlInputs()[0], "https://example.org");
      await fixture.whenStable();
      expect(component.activityForm().valid()).toBe(true);
    });
  });

  describe("schema constraints (FastTrackActivityModelSchema)", () => {
    it("is fully valid once every required field is set (baseline for the tests below)", () => {
      fillEveryRequiredField();
      expect(component.activityForm().valid()).toBe(true);
    });

    it("is invalid when title is empty", () => {
      fillEveryRequiredField();
      const title = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      setNativeValue(fixture, title, "");
      expect(component.activityForm().valid()).toBe(false);
    });

    it("is invalid when contact is empty", () => {
      fillEveryRequiredField();
      referenceSelectIn(fixture, "contact").value.set([]);
      fixture.detectChanges();
      expect(component.activityForm().valid()).toBe(false);
    });

    it("is invalid when responsibleUnit is empty", () => {
      fillEveryRequiredField();
      referenceSelectIn(fixture, "Activity.responsibleUnit").value.set([]);
      fixture.detectChanges();
      expect(component.activityForm().valid()).toBe(false);
    });

    it("stays valid with all optional fields left at their defaults", () => {
      fillEveryRequiredField();
      const m = component.model();
      expect(m.shortName).toBe("");
      expect(m.involvedPerson).toEqual([]);
      expect(m.involvedUnit).toEqual([]);
      expect(m.funderOrCommissioner).toEqual([]);
      expect(m.website).toEqual([]);
      expect(m.start).toBeNull();
      expect(m.end).toBeNull();
      expect(component.activityForm().valid()).toBe(true);
    });
  });

  describe("fills every wired field and checks the whole model", () => {
    it("ends up with the expected model after filling every field the UI currently supports", async () => {
      const title = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      setNativeValue(fixture, title, "Sentinel surveillance project");
      const shortName = fieldsetEl(fixture, "shortName").query(By.css("input")).nativeElement;
      setNativeValue(fixture, shortName, "SSP");
      const abstract = fieldsetEl(fixture, "abstract").query(By.css("textarea")).nativeElement;
      setNativeValue(fixture, abstract, "An activity abstract");

      const contact = VALID_CONTACT_POINT("contact-1", "info@example.org");
      referenceSelectIn(fixture, "contact").value.set([contact]);
      const involvedPerson = VALID_PERSON("person-1", "Jane Doe");
      referenceSelectIn(fixture, "Activity.involvedPerson").value.set([involvedPerson]);
      const responsibleUnit = VALID_ORG_UNIT("unit-1", "RKI");
      referenceSelectIn(fixture, "Activity.responsibleUnit").value.set([responsibleUnit]);
      const involvedUnit = VALID_ORG_UNIT("unit-2", "Dept X");
      referenceSelectIn(fixture, "Activity.involvedUnit").value.set([involvedUnit]);
      const funder = VALID_ORGANIZATION("org-1", "Funding Org");
      referenceSelectIn(fixture, "Activity.funderOrCommissioner").value.set([funder]);

      const select = await loader.getHarness(
        MatSelectHarness.with({ selector: `[data-testid="activityType-select"]` }),
      );
      await select.open();
      await select.clickOptions({ text: "Type 1" });

      const websiteEl = fieldsetEl(fixture, "website").nativeElement as HTMLElement;
      iconButton(websiteEl, "add").click();
      await fixture.whenStable();
      setNativeValue(
        fixture,
        websiteEl.querySelector<HTMLInputElement>("li.row input[type=url]")!,
        "https://example.org",
      );

      TestBed.inject(TranslocoService).setActiveLang("en");
      fixture.detectChanges();
      const { start, end } = await datepickerInputs(loader);
      await start.setValue("01/01/2026");
      await end.setValue("12/31/2026");

      const model = component.model();
      expect(model.title).toBe("Sentinel surveillance project");
      expect(model.shortName).toBe("SSP");
      expect(model.abstract).toBe("An activity abstract");
      expect(model.contact).toEqual([contact]);
      expect(model.involvedPerson).toEqual([involvedPerson]);
      expect(model.responsibleUnit).toEqual([responsibleUnit]);
      expect(model.involvedUnit).toEqual([involvedUnit]);
      expect(model.funderOrCommissioner).toEqual([funder]);
      expect(model.activityType).toEqual([ACTIVITY_TYPE_ID]);
      expect(model.website).toHaveLength(1);
      expect(model.website[0].url).toBe("https://example.org");
      expect(model.start?.toISODate()).toBe("2026-01-01");
      expect(model.end?.toISODate()).toBe("2026-12-31");

      expect(component.activityForm().valid()).toBe(true);
    });
  });

  describe("form submission", () => {
    it("submits the valid model and handles a successful response", async () => {
      fillEveryRequiredField();
      const expectedModel = component.model();

      const submission = TestBed.inject(FastTrackSubmission);
      const router = TestBed.inject(Router);
      const notifier = TestBed.inject(ToastNotifier);

      vi.spyOn(router, "navigate").mockResolvedValue(true);
      vi.mocked(submission.submit).mockResolvedValue({
        success: true,
        response: { $type: "ActivityRuleSetResponse", stableTargetId: "activity-123" },
      } as Awaited<ReturnType<FastTrackSubmission["submit"]>>);

      await submitForm();

      expect(component.activityForm().valid()).toBe(true);
      expect(submission.submit).toHaveBeenCalledOnce();
      expect(submission.submit).toHaveBeenCalledWith(expectedModel);
      expect(router.navigate).toHaveBeenCalledWith(["edit", "activity-123"]);
      expect(notifier.success).toHaveBeenCalledWith(
        { msgKey: "fasttrack.activity.toast.success.message" },
        { msgKey: "fasttrack.activity.toast.success.title" },
      );
      expect(notifier.error).not.toHaveBeenCalled();
    });

    it("passes a failed submission result to the failure notifier", async () => {
      fillEveryRequiredField();

      const submission = TestBed.inject(FastTrackSubmission);
      const router = TestBed.inject(Router);
      const notifier = TestBed.inject(ToastNotifier);

      vi.spyOn(router, "navigate").mockResolvedValue(true);

      const submitError = new SubmissionError({ $type: "ActivityRuleSetRequest", additive: {} });
      const submitResult = {
        success: false,
        error: submitError,
      } as Awaited<ReturnType<FastTrackSubmission["submit"]>>;
      vi.mocked(submission.submit).mockResolvedValue(submitResult);

      await submitForm();

      expect(component.activityForm().valid()).toBe(true);
      expect(submission.submit).toHaveBeenCalledOnce();
      expect(notifier.submissionError).toHaveBeenCalledWith(
        { msgKey: "fasttrack.activity.toast.submissionError.message" },
        { msgKey: "fasttrack.activity.toast.submissionError.title" },
        submitError,
      );
      expect(router.navigate).not.toHaveBeenCalled();
      expect(notifier.success).not.toHaveBeenCalled();
    });

    it("does not submit when required fields are missing", async () => {
      const submission = TestBed.inject(FastTrackSubmission);

      await submitForm();

      expect(component.activityForm().valid()).toBe(false);
      expect(submission.submit).not.toHaveBeenCalled();
    });

    it("focuses the first invalid control when submitting an invalid form", async () => {
      vi.spyOn(console, "log").mockImplementation(() => undefined);

      await submitForm();

      const titleInput = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      expect(document.activeElement).toBe(titleInput);
    });

    it("does not show the saving state when idle", () => {
      const button = fixture.nativeElement.querySelector(
        'button[type="submit"]',
      ) as HTMLButtonElement;
      expect(button.disabled).toBe(false);
      expect(button.querySelector("mat-progress-spinner")).toBeNull();
      expect(button.textContent?.trim()).toBe(
        TestBed.inject(TranslocoService).translate("fasttrack.activity.save-button.label"),
      );
    });

    it("disables the submit button and shows a spinner while submitting", async () => {
      fillEveryRequiredField();

      const submission = TestBed.inject(FastTrackSubmission);
      const router = TestBed.inject(Router);

      vi.spyOn(router, "navigate").mockResolvedValue(true);

      // Keep the submission pending so we can inspect the loading state.
      let resolveSubmit!: (result: Awaited<ReturnType<FastTrackSubmission["submit"]>>) => void;

      vi.mocked(submission.submit).mockReturnValue(
        new Promise((resolve) => {
          resolveSubmit = resolve;
        }),
      );

      const form = fixture.nativeElement.querySelector("form") as HTMLFormElement;
      const submitButton = form.querySelector('button[type="submit"]') as HTMLButtonElement;

      expect(submitButton).toBeTruthy();
      expect(submitButton.disabled).toBe(false);

      // Trigger submission, but don't resolve the promise yet.
      form.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));

      // Let the async submission action start and render its pending state.
      await Promise.resolve();
      fixture.detectChanges();
      await fixture.whenStable();

      // Assert the loading UI.
      expect(submitButton.disabled).toBe(true);
      expect(submitButton.querySelector("mat-progress-spinner")).not.toBeNull();

      // Finish the pending submission to cleanly complete the test.
      resolveSubmit({
        success: false,
        error: new SubmissionError({ $type: "ActivityRuleSetRequest" }),
      });

      await vi.waitFor(() => expect(component.activityForm().submitting()).toBe(false));

      fixture.detectChanges();
      await fixture.whenStable();

      expect(submitButton.disabled).toBe(false);
      expect(submitButton.querySelector("mat-progress-spinner")).toBeNull();
    });
  });

  describe("enter key handling", () => {
    const pressEnter = (el: HTMLElement) => {
      const event = new KeyboardEvent("keydown", { key: "Enter", bubbles: true, cancelable: true });
      el.dispatchEvent(event);
      return event;
    };

    it("prevents the default action for Enter in single-line inputs (no accidental submit)", () => {
      const input = fieldsetEl(fixture, "title").query(By.css("input")).nativeElement;
      expect(pressEnter(input).defaultPrevented).toBe(true);
    });

    it("keeps Enter working as a line break in the abstract textarea", () => {
      const textarea = fieldsetEl(fixture, "abstract").query(By.css("textarea")).nativeElement;
      expect(pressEnter(textarea).defaultPrevented).toBe(false);
    });
  });
});
