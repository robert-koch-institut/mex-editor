import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { TestBed } from "@angular/core/testing";
import { MatIconHarness } from "@angular/material/icon/testing";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { By } from "@angular/platform-browser";
import { vi } from "vitest";

import { ErrorMailToPipe } from "../error-mail-to-pipe";
import type { SubmissionFailure } from "../models/submission-result";
import { SubmissionFailureToast } from "./submission-failure-toast";

const failure: SubmissionFailure<unknown> = {
  success: false,
  payload: { $type: "ResourceRuleSetRequest", additive: { title: [{ value: "Titel" }] } },
  error: new Error("boom"),
};

describe("SubmissionFailureToast", () => {
  function setup() {
    const snackBarRef = { dismiss: vi.fn(), dismissWithAction: vi.fn() };
    TestBed.configureTestingModule({
      imports: [SubmissionFailureToast],
      providers: [
        {
          provide: MAT_SNACK_BAR_DATA,
          useValue: { title: "Fehler", message: "Speichern fehlgeschlagen.", failure },
        },
        { provide: MatSnackBarRef, useValue: snackBarRef },
      ],
    });
    const fixture = TestBed.createComponent(SubmissionFailureToast);
    fixture.detectChanges();
    const link = fixture.debugElement.query(By.css(".toast-actions a"))?.nativeElement as
      HTMLAnchorElement | undefined;
    return { fixture, snackBarRef, link, loader: TestbedHarnessEnvironment.loader(fixture) };
  }

  it("shows title and message from the snackbar data", () => {
    const { fixture } = setup();

    const text = (fixture.nativeElement as HTMLElement).textContent;
    expect(text).toContain("Fehler");
    expect(text).toContain("Speichern fehlgeschlagen.");
  });

  it("uses the error icon", async () => {
    const { loader } = setup();

    const icon = await loader.getHarness(MatIconHarness.with({ selector: ".toast-icon" }));
    expect(await icon.getName()).toBe("error");
  });

  it("offers a mail link inside the toast's content area", () => {
    const { fixture } = setup();

    expect(fixture.debugElement.query(By.css(".toast-content .toast-actions a"))).not.toBeNull();
  });

  it("links to the exact mailto URL the errorMailTo pipe builds for the failure", () => {
    const { link } = setup();

    // would be rewritten to "unsafe:mailto:..." if Angular's URL sanitizer rejected the link
    expect(link!.getAttribute("href")).toBe(new ErrorMailToPipe().transform(failure));
    expect(link!.getAttribute("href")).toMatch(/^mailto:Mex@rki\.de\?/);
  });

  it("shows a (non-empty) label on the link", () => {
    const { link } = setup();

    expect(link!.textContent?.trim()).not.toBe("");
  });

  it("dismisses the snackbar WITH action when the link is clicked", () => {
    const { link, snackBarRef } = setup();
    link!.addEventListener("click", (event) => event.preventDefault()); // don't let jsdom try to navigate

    link!.click();

    expect(snackBarRef.dismissWithAction).toHaveBeenCalledTimes(1);
    expect(snackBarRef.dismiss).not.toHaveBeenCalled();
  });

  it("dismisses WITHOUT action when the close button is clicked", () => {
    const { fixture, snackBarRef } = setup();

    (fixture.debugElement.query(By.css(".toast-close")).nativeElement as HTMLButtonElement).click();

    expect(snackBarRef.dismiss).toHaveBeenCalledTimes(1);
    expect(snackBarRef.dismissWithAction).not.toHaveBeenCalled();
  });
});
