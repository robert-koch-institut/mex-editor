import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { FigmaTestPage } from "./figma-test-page";

describe("FigmaTestPage", () => {
  let component: FigmaTestPage;
  let fixture: ComponentFixture<FigmaTestPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FigmaTestPage],
    }).compileComponents();

    fixture = TestBed.createComponent(FigmaTestPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("applies surface-variant colors to key elements", async () => {
    // set CSS variables on :root so component styles resolve to known values
    const root = document.documentElement;
    const color = "rgb(10,20,30)";
    root.style.setProperty("--mat-sys-surface-variant", color);
    root.style.setProperty("--mat-sys-on-surface", "rgb(240,240,240)");
    // set some common Material intermediate variables so var(...) fallbacks resolve
    const auxVars = [
      "--mat-fab-small-container-color",
      "--mat-button-filled-container-color",
      "--mat-sys-primary-container",
      "--mat-fab-container-color",
    ];
    for (const v of auxVars) root.style.setProperty(v, color);

    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement as HTMLElement;

    const miniFab = el.querySelector("button[matMiniFab]") as HTMLElement | null;
    const filled = el.querySelector('button[matButton="filled"]') as HTMLElement | null;
    const toggle = el.querySelector("mat-button-toggle") as HTMLElement | null;

    // helper to read computed background-color
    const bgRaw = (node: Element | null) =>
      node ? getComputedStyle(node as Element).backgroundColor : null;

    // Resolve var(...) expressions recursively by reading from :root.
    // Uses a paren-depth scan instead of a regex, because a plain regex
    // like /var\(...\)/ can't correctly match nested var(...) fallbacks
    // (e.g. var(--a, var(--b, var(--c)))) — a regex with `[^)]+` for the
    // fallback stops at the FIRST `)`, so it only ever matches up through
    // the innermost close-paren. The outer close-parens are then left
    // dangling in the string after replace(), which is exactly why the
    // original test produced "rgb(10,20,30))" with a trailing extra `)`.
    const resolveVar = (value: string | null): string | null => {
      if (!value) return value;

      const findVarCall = (input: string) => {
        const idx = input.indexOf("var(");
        if (idx === -1) return null;
        let depth = 0;
        let end = -1;
        for (let i = idx + 3; i < input.length; i++) {
          if (input[i] === "(") depth++;
          else if (input[i] === ")") {
            depth--;
            if (depth === 0) {
              end = i;
              break;
            }
          }
        }
        if (end === -1) return null;
        const inner = input.slice(idx + 4, end);
        return { idx, end, inner };
      };

      const splitNameFallback = (inner: string) => {
        let commaIdx = -1;
        let depth = 0;
        for (let i = 0; i < inner.length; i++) {
          if (inner[i] === "(") depth++;
          else if (inner[i] === ")") depth--;
          else if (inner[i] === "," && depth === 0) {
            commaIdx = i;
            break;
          }
        }
        const varName = (commaIdx === -1 ? inner : inner.slice(0, commaIdx)).trim();
        const fallback = commaIdx === -1 ? "" : inner.slice(commaIdx + 1).trim();
        return { varName, fallback };
      };

      const resolveOnce = (input: string): string => {
        const call = findVarCall(input);
        if (!call) return input;
        const { idx, end, inner } = call;
        const { varName, fallback } = splitNameFallback(inner);
        const resolved = getComputedStyle(document.documentElement)
          .getPropertyValue(varName)
          .trim();
        const replacement = resolved || fallback;
        const resolvedReplacement = replacement ? resolveOnce(replacement) : "";
        const next = input.slice(0, idx) + resolvedReplacement + input.slice(end + 1);
        return resolveOnce(next);
      };

      return resolveOnce(value).trim();
    };

    expect(resolveVar(bgRaw(miniFab))).toBe("rgb(10,20,30)");
    expect(resolveVar(bgRaw(filled))).toBe("rgb(10,20,30)");
    expect(resolveVar(bgRaw(toggle))).toBe("transparent");
  });
});
