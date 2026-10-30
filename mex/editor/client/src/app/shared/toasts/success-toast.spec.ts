import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { TestBed } from "@angular/core/testing";
import { MatIconHarness } from "@angular/material/icon/testing";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { By } from "@angular/platform-browser";
import { vi } from "vitest";

import { SuccessToast } from "./success-toast";

describe("SuccessToast", () => {
  function setup() {
    TestBed.configureTestingModule({
      imports: [SuccessToast],
      providers: [
        { provide: MAT_SNACK_BAR_DATA, useValue: { title: "Gespeichert", message: "Alles klar." } },
        { provide: MatSnackBarRef, useValue: { dismiss: vi.fn() } },
      ],
    });
    const fixture = TestBed.createComponent(SuccessToast);
    fixture.detectChanges();
    return { fixture, loader: TestbedHarnessEnvironment.loader(fixture) };
  }

  it("shows title and message from the snackbar data", () => {
    const { fixture } = setup();

    const text = (fixture.nativeElement as HTMLElement).textContent;
    expect(text).toContain("Gespeichert");
    expect(text).toContain("Alles klar.");
  });

  it("uses the check_circle icon", async () => {
    const { loader } = setup();

    const icon = await loader.getHarness(MatIconHarness.with({ selector: ".toast-icon" }));
    expect(await icon.getName()).toBe("check_circle");
  });

  it("is built on mex-toast-content", () => {
    const { fixture } = setup();

    expect(fixture.debugElement.query(By.css("mex-toast-content"))).not.toBeNull();
  });
});
