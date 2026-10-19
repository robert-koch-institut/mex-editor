import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { TestBed } from "@angular/core/testing";
import { MatIconHarness } from "@angular/material/icon/testing";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { By } from "@angular/platform-browser";
import { vi } from "vitest";

import { ErrorToast } from "./error-toast";

describe("ErrorToast", () => {
  function setup() {
    TestBed.configureTestingModule({
      imports: [ErrorToast],
      providers: [
        {
          provide: MAT_SNACK_BAR_DATA,
          useValue: {
            title: "Fehler",
            message: "Das hat nicht geklappt.",
            error: new Error("boom"),
          },
        },
        { provide: MatSnackBarRef, useValue: { dismiss: vi.fn() } },
      ],
    });
    const fixture = TestBed.createComponent(ErrorToast);
    fixture.detectChanges();
    return { fixture, loader: TestbedHarnessEnvironment.loader(fixture) };
  }

  it("shows title and message from the snackbar data", () => {
    const { fixture } = setup();

    const text = (fixture.nativeElement as HTMLElement).textContent;
    expect(text).toContain("Fehler");
    expect(text).toContain("Das hat nicht geklappt.");
  });

  it("uses the error icon", async () => {
    const { loader } = setup();

    const icon = await loader.getHarness(MatIconHarness.with({ selector: ".toast-icon" }));
    expect(await icon.getName()).toBe("error");
  });

  it("does not show the technical error details to the user", () => {
    const { fixture } = setup();

    expect((fixture.nativeElement as HTMLElement).textContent).not.toContain("boom");
  });

  it("is built on mex-toast-content", () => {
    const { fixture } = setup();

    expect(fixture.debugElement.query(By.css("mex-toast-content"))).not.toBeNull();
  });
});
