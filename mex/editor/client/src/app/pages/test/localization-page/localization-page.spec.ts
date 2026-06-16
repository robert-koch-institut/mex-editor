import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LocalizationPage } from "./localization-page";
import { getTranslocoTestingModule } from "../../../transloco";
import { TranslocoService } from "@jsverse/transloco";

describe("LocalizationPage", () => {
  let component: LocalizationPage;
  let fixture: ComponentFixture<LocalizationPage>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LocalizationPage, getTranslocoTestingModule()],
      providers: [

      ],
    }).compileComponents();
    fixture = TestBed.createComponent(LocalizationPage);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should render text in german", () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector("[data-testid='headline']")?.textContent).toBe("Titelzeile");
    expect(compiled.querySelector("[data-testid='date']")?.textContent).toBe("1.1.2000");
    expect(compiled.querySelector("[data-testid='datetime']")?.textContent).toBe("01.01.2000, 12:30:00");
    expect(compiled.querySelector("[data-testid='decimal']")?.textContent).toBe("213,123");
    expect(compiled.querySelector("[data-testid='money']")?.textContent).toBe("100.000,12 €");
    expect(compiled.querySelector("[data-testid='singular']")?.textContent).toBe("EINER");
    expect(compiled.querySelector("[data-testid='plural']")?.textContent).toBe("VIELE");
  })


  it("should render text in english", () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const transloco = TestBed.inject(TranslocoService);
    transloco.setActiveLang("en");
    fixture.detectChanges();

    expect(compiled.querySelector("[data-testid='headline']")?.textContent).toBe("Headline");
    expect(compiled.querySelector("[data-testid='date']")?.textContent).toBe("1/1/2000");
    expect(compiled.querySelector("[data-testid='datetime']")?.textContent).toBe("Jan 1, 2000, 12:30:00 PM");
    expect(compiled.querySelector("[data-testid='decimal']")?.textContent).toBe("213.123");
    expect(compiled.querySelector("[data-testid='money']")?.textContent).toBe("$100,000.12");
    expect(compiled.querySelector("[data-testid='singular']")?.textContent).toBe("ONE");
    expect(compiled.querySelector("[data-testid='plural']")?.textContent).toBe("MANY");
  })
});
