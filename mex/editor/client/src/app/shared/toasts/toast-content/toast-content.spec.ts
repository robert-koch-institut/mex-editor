import { TestbedHarnessEnvironment } from "@angular/cdk/testing/testbed";
import { Component } from "@angular/core";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { MatButtonHarness } from "@angular/material/button/testing";
import { MatIconHarness } from "@angular/material/icon/testing";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";
import { By } from "@angular/platform-browser";
import { vi } from "vitest";

import type { ToastData } from "../toast-data";
import { ToastContent } from "./toast-content";

const DEFAULT_DATA: ToastData = {
  title: "Gespeichert",
  message: "Die Resource wurde erfolgreich gespeichert.",
};

/** Creates ToastContent the way MatSnackBar does: data + ref come in via DI. */
function setup(data: ToastData = DEFAULT_DATA, iconName = "check_circle") {
  const snackBarRef = { dismiss: vi.fn() };
  TestBed.configureTestingModule({
    imports: [ToastContent],
    providers: [
      { provide: MAT_SNACK_BAR_DATA, useValue: data },
      { provide: MatSnackBarRef, useValue: snackBarRef },
    ],
  });
  const fixture: ComponentFixture<ToastContent> = TestBed.createComponent(ToastContent);
  fixture.componentRef.setInput("iconName", iconName);
  fixture.detectChanges();
  const loader = TestbedHarnessEnvironment.loader(fixture);
  const text = (selector: string) =>
    (fixture.debugElement.query(By.css(selector)).nativeElement as HTMLElement).textContent;
  return { fixture, snackBarRef, loader, text };
}

// eslint-disable-next-line max-lines-per-function
describe("ToastContent", () => {
  describe("title and message", () => {
    it("shows the title", () => {
      const { text } = setup();

      expect(text(".toast-title")).toBe("Gespeichert");
    });

    it("shows the message", () => {
      const { text } = setup();

      expect(text(".toast-message")).toBe("Die Resource wurde erfolgreich gespeichert.");
    });

    it("renders title and message as plain text, not as HTML", () => {
      const { fixture, text } = setup({
        title: "<i>Titel</i>",
        message: "<b>fett</b> & <script>x</script>",
      });

      expect(text(".toast-title")).toBe("<i>Titel</i>");
      expect(text(".toast-message")).toBe("<b>fett</b> & <script>x</script>");
      expect(fixture.debugElement.query(By.css("b, i, script"))).toBeNull();
    });

    it("keeps empty title/message elements in place (stable layout) when they are empty", () => {
      const { fixture, text } = setup({ title: "", message: "" });

      expect(fixture.debugElement.query(By.css(".toast-title"))).not.toBeNull();
      expect(fixture.debugElement.query(By.css(".toast-message"))).not.toBeNull();
      expect(text(".toast-title")).toBe("");
      expect(text(".toast-message")).toBe("");
    });

    it("does not shorten a long message in the DOM", () => {
      const long = "Fehler ".repeat(200).trim();
      const { text } = setup({ title: "Fehler", message: long });

      expect(text(".toast-message")).toBe(long);
    });
  });

  describe("icon", () => {
    it("shows the icon given via the iconName input", async () => {
      const { loader } = setup(DEFAULT_DATA, "check_circle");

      const icon = await loader.getHarness(MatIconHarness.with({ selector: ".toast-icon" }));
      expect(await icon.getName()).toBe("check_circle");
    });

    it("follows changes of the iconName input", async () => {
      const { fixture, loader } = setup(DEFAULT_DATA, "check_circle");

      fixture.componentRef.setInput("iconName", "error");
      fixture.detectChanges();

      const icon = await loader.getHarness(MatIconHarness.with({ selector: ".toast-icon" }));
      expect(await icon.getName()).toBe("error");
    });
  });

  describe("close button", () => {
    it("is accessible: German aria-label and type=button (never submits a surrounding form)", async () => {
      const { loader } = setup();

      const button = await loader.getHarness(MatButtonHarness.with({ selector: ".toast-close" }));
      const host = await button.host();
      expect(await host.getAttribute("aria-label")).toBe("Schließen");
      expect(await host.getAttribute("type")).toBe("button");
    });

    it("shows the 'close' icon", async () => {
      const { loader } = setup();

      const icon = await loader.getHarness(MatIconHarness.with({ ancestor: ".toast-close" }));
      expect(await icon.getName()).toBe("close");
    });

    it("does not dismiss the snackbar on its own", () => {
      const { snackBarRef } = setup();

      expect(snackBarRef.dismiss).not.toHaveBeenCalled();
    });

    it("dismisses the snackbar exactly once when clicked", async () => {
      const { loader, snackBarRef } = setup();

      const button = await loader.getHarness(MatButtonHarness.with({ selector: ".toast-close" }));
      await button.click();

      expect(snackBarRef.dismiss).toHaveBeenCalledTimes(1);
    });
  });

  describe("layout", () => {
    it("has icon, title and close button in the header, in this order", () => {
      const { fixture } = setup();

      const header = fixture.debugElement.query(By.css(".toast-header"))
        .nativeElement as HTMLElement;
      const known = ["toast-icon", "toast-title", "toast-close"];
      // Material adds its own classes to mat-icon / mat-icon-button, so look for ours specifically
      const order = Array.from(header.children).map((c) =>
        known.find((k) => c.classList.contains(k)),
      );
      expect(order).toEqual(known);
    });

    it("has the message before the projected content in the body", () => {
      const { fixture } = setup();

      const body = fixture.debugElement.query(By.css(".toast-body")).nativeElement as HTMLElement;
      expect(Array.from(body.children).map((c) => c.className)).toEqual([
        "toast-message",
        "toast-content",
      ]);
    });
  });

  describe("content projection", () => {
    @Component({
      imports: [ToastContent],
      template: `<mex-toast-content iconName="error"
        ><a class="projected" href="#">Mehr erfahren</a></mex-toast-content
      >`,
    })
    class Host {}

    it("renders projected content inside .toast-content", () => {
      TestBed.configureTestingModule({
        imports: [Host],
        providers: [
          { provide: MAT_SNACK_BAR_DATA, useValue: DEFAULT_DATA },
          { provide: MatSnackBarRef, useValue: { dismiss: vi.fn() } },
        ],
      });
      const fixture = TestBed.createComponent(Host);
      fixture.detectChanges();

      const projected = fixture.debugElement.query(By.css(".toast-content .projected"));
      expect(projected).not.toBeNull();
      expect((projected.nativeElement as HTMLElement).textContent).toBe("Mehr erfahren");
    });

    it("renders an empty .toast-content when nothing is projected", () => {
      const { fixture } = setup();

      const content = fixture.debugElement.query(By.css(".toast-content"))
        .nativeElement as HTMLElement;
      expect(content.children).toHaveLength(0);
      expect(content.textContent?.trim()).toBe("");
    });
  });
});
