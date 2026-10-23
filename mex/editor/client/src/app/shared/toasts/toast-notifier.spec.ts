import { TestBed } from "@angular/core/testing";
import { MatSnackBar } from "@angular/material/snack-bar";
import { firstValueFrom } from "rxjs";
import { vi } from "vitest";

import type { SubmissionFailure } from "../models/submission-result";
import { ErrorToast } from "./error-toast";
import { SubmissionFailureToast } from "./submission-failure-toast";
import { SuccessToast } from "./success-toast";
import { ToastNotifier } from "./toast-notifier";

const failure: SubmissionFailure<unknown> = {
  success: false,
  payload: { $type: "ResourceRuleSetRequest" },
  error: new Error("boom"),
};

// eslint-disable-next-line max-lines-per-function
describe("ToastNotifier", () => {
  // eslint-disable-next-line max-lines-per-function
  describe("what it asks MatSnackBar to open", () => {
    let notifier: ToastNotifier;
    let openFromComponent: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      openFromComponent = vi.fn();
      TestBed.configureTestingModule({
        providers: [{ provide: MatSnackBar, useValue: { openFromComponent } }],
      });
      notifier = TestBed.inject(ToastNotifier);
    });

    const lastCall = () => {
      const [component, config] = openFromComponent.mock.calls.at(-1)!;
      return { component, config };
    };

    describe("success()", () => {
      it("opens a SuccessToast", () => {
        notifier.success("Nachricht", "Titel");

        expect(openFromComponent).toHaveBeenCalledTimes(1);
        expect(lastCall().component).toBe(SuccessToast);
      });

      it("passes title and message to the toast (note: the message is the FIRST argument)", () => {
        notifier.success("die Nachricht", "der Titel");

        expect(lastCall().config.data).toEqual({ title: "der Titel", message: "die Nachricht" });
      });

      it("shows for 4 seconds by default", () => {
        notifier.success("m", "t");

        expect(lastCall().config.duration).toBe(4000);
      });

      it("accepts a custom duration", () => {
        notifier.success("m", "t", 1500);

        expect(lastCall().config.duration).toBe(1500);
      });

      it("positions the toast at the bottom end of the screen", () => {
        notifier.success("m", "t");

        expect(lastCall().config).toMatchObject({
          horizontalPosition: "end",
          verticalPosition: "bottom",
        });
      });

      it("styles it with the 'toast' and 'success-toast' panel classes", () => {
        notifier.success("m", "t");

        expect(lastCall().config.panelClass).toEqual(["toast", "success-toast"]);
      });
    });

    describe("error()", () => {
      it("opens an ErrorToast", () => {
        notifier.error("Nachricht", "Titel", new Error("boom"));

        expect(lastCall().component).toBe(ErrorToast);
      });

      it("passes title, message and the error to the toast", () => {
        const error = new Error("boom");

        notifier.error("die Nachricht", "der Titel", error);

        expect(lastCall().config.data).toEqual({
          title: "der Titel",
          message: "die Nachricht",
          error,
        });
        expect(lastCall().config.data.error).toBe(error);
      });

      it("shows for 10 seconds by default (longer than a success)", () => {
        notifier.error("m", "t", new Error("x"));

        expect(lastCall().config.duration).toBe(10000);
      });

      it("accepts a custom duration", () => {
        notifier.error("m", "t", new Error("x"), 500);

        expect(lastCall().config.duration).toBe(500);
      });

      it("styles it with the 'toast' and 'error-toast' panel classes and the same position", () => {
        notifier.error("m", "t", new Error("x"));

        expect(lastCall().config.panelClass).toEqual(["toast", "error-toast"]);
        expect(lastCall().config).toMatchObject({
          horizontalPosition: "end",
          verticalPosition: "bottom",
        });
      });
    });

    describe("submissionFailure()", () => {
      it("opens a SubmissionFailureToast", () => {
        notifier.submissionFailure("Nachricht", "Titel", failure);

        expect(lastCall().component).toBe(SubmissionFailureToast);
      });

      it("passes title, message and the failure to the toast", () => {
        notifier.submissionFailure("die Nachricht", "der Titel", failure);

        expect(lastCall().config.data).toEqual({
          title: "der Titel",
          message: "die Nachricht",
          failure,
        });
        expect(lastCall().config.data.failure).toBe(failure);
      });

      it("shows for 10 seconds by default, with the error styling", () => {
        notifier.submissionFailure("m", "t", failure);

        expect(lastCall().config.duration).toBe(10000);
        expect(lastCall().config.panelClass).toEqual(["toast", "error-toast"]);
      });

      it("accepts a custom duration", () => {
        notifier.submissionFailure("m", "t", failure, 2500);

        expect(lastCall().config.duration).toBe(2500);
      });
    });

    it("builds a fresh config per call (a later toast cannot leak into an earlier one's config)", () => {
      notifier.success("m1", "t1");
      notifier.error("m2", "t2", new Error("x"));

      const [[, first], [, second]] = openFromComponent.mock.calls;
      expect(first).not.toBe(second);
      expect(first.panelClass).toEqual(["toast", "success-toast"]);
      expect(first.data).toEqual({ title: "t1", message: "m1" });
      expect(second.panelClass).toEqual(["toast", "error-toast"]);
    });
  });

  describe("rendered with the real MatSnackBar", () => {
    let notifier: ToastNotifier;
    let snackBar: MatSnackBar;
    let openSpy: ReturnType<typeof vi.spyOn>;

    beforeEach(() => {
      notifier = TestBed.inject(ToastNotifier);
      snackBar = TestBed.inject(MatSnackBar);
      openSpy = vi.spyOn(snackBar, "openFromComponent");
    });

    afterEach(() => {
      snackBar.dismiss();
    });

    const toastText = (selector: string) => document.querySelector(selector)?.textContent;
    const lastRef = () =>
      openSpy.mock.results.at(-1)!.value as ReturnType<MatSnackBar["openFromComponent"]>;

    it("shows a success toast with icon, title and message", async () => {
      notifier.success("Die Resource wurde gespeichert.", "Gespeichert");

      await vi.waitFor(() => expect(toastText(".toast-title")).toBe("Gespeichert"));
      expect(toastText(".toast-message")).toBe("Die Resource wurde gespeichert.");
      expect(toastText(".toast-icon")).toBe("check_circle");
    });

    it("shows an error toast with the error icon", async () => {
      notifier.error("Das hat nicht geklappt.", "Fehler", new Error("boom"));

      await vi.waitFor(() => expect(toastText(".toast-title")).toBe("Fehler"));
      expect(toastText(".toast-message")).toBe("Das hat nicht geklappt.");
      expect(toastText(".toast-icon")).toBe("error");
    });

    it("applies the panel classes to the rendered snackbar", async () => {
      notifier.success("m", "t");

      await vi.waitFor(() => expect(document.querySelector(".toast.success-toast")).not.toBeNull());
      expect(document.querySelector(".error-toast")).toBeNull();
    });

    it("shows a submission-failure toast with a mailto link", async () => {
      notifier.submissionFailure("Speichern fehlgeschlagen.", "Fehler", failure);

      await vi.waitFor(() => expect(document.querySelector(".toast-actions a")).not.toBeNull());
      const href = document.querySelector(".toast-actions a")!.getAttribute("href");
      expect(href).toMatch(/^mailto:Mex@rki\.de\?subject=/);
    });

    it("dismisses (not by action) when the close button is clicked", async () => {
      notifier.success("m", "t");
      await vi.waitFor(() => expect(document.querySelector(".toast-close")).not.toBeNull());

      (document.querySelector(".toast-close") as HTMLButtonElement).click();

      expect(await firstValueFrom(lastRef().afterDismissed())).toEqual({
        dismissedByAction: false,
      });
    });

    it("dismisses WITH action when the mail link is clicked", async () => {
      notifier.submissionFailure("m", "t", failure);
      await vi.waitFor(() => expect(document.querySelector(".toast-actions a")).not.toBeNull());
      const link = document.querySelector(".toast-actions a") as HTMLAnchorElement;
      link.addEventListener("click", (event) => event.preventDefault()); // no real navigation in jsdom

      link.click();

      expect(await firstValueFrom(lastRef().afterDismissed())).toEqual({ dismissedByAction: true });
    });

    it("replaces the previous toast when a new one is shown (MatSnackBar shows one at a time)", async () => {
      notifier.success("erste", "Erste");
      await vi.waitFor(() => expect(toastText(".toast-title")).toBe("Erste"));
      const firstRef = lastRef();

      notifier.error("zweite", "Zweite", new Error("x"));

      expect(await firstValueFrom(firstRef.afterDismissed())).toBeDefined();
      await vi.waitFor(() => expect(toastText(".toast-title")).toBe("Zweite"));
      expect(document.querySelectorAll(".toast-title")).toHaveLength(1);
    });
  });
});
