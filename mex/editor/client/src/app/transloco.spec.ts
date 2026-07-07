import type { TranslocoTestingOptions } from "@jsverse/transloco";
import { TranslocoDirective, TranslocoService, TranslocoTestingModule } from "@jsverse/transloco";
import { translocoProviders, translocoConfig } from "./transloco";
import { Component } from "@angular/core";
import { TranslocoDatePipe, TranslocoCurrencyPipe, TranslocoDecimalPipe } from "@jsverse/transloco-locale";
import type { ComponentFixture} from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

/* eslint-disable @typescript-eslint/naming-convention */
const de = {
  "test.headline": "Titelzeile",
  "test.icuMessageFormat": "{count, plural, one {EINER} other {VIELE}}",
};

const en = {
  "test.headline": "Headline",
  "test.icuMessageFormat": "{count, plural, one {ONE} other {MANY}}",
};
/* eslint-enable @typescript-eslint/naming-convention */

/**
 * Creates the transloco testing module include all necessary providers.
 * @param options addition option for testing purposes.
 * @returns transloco testing module including all necessary providers.
 */
function getTranslocoTestingModule(options: TranslocoTestingOptions = {}) {
  const testModule = TranslocoTestingModule.forRoot({
    langs: { de, en },
    translocoConfig,
    preloadLangs: true,
    ...options,
  });
  testModule.providers?.push(...translocoProviders);
  return testModule;
}

@Component({
  selector: "app-localization-page",
  imports: [TranslocoDirective, TranslocoDatePipe, TranslocoCurrencyPipe, TranslocoDecimalPipe],
  template: `
    <ng-container *transloco="let t">
      <h1 data-testid="headline">{{ t("test.headline") }}</h1>
      <div data-testid="date">{{ date | translocoDate }}</div>
      <div data-testid="datetime">
        {{ datetime | translocoDate: { dateStyle: "medium", timeStyle: "medium" } }}
      </div>
      <div data-testid="decimal">{{ decimal | translocoDecimal }}</div>
      <div data-testid="money">{{ money | translocoCurrency }}</div>
      <div data-testid="singular">{{ t("test.icuMessageFormat", { count: 1 }) }}</div>
      <div data-testid="plural">{{ t("test.icuMessageFormat", { count: 3 }) }}</div>
    </ng-container>
  `,
})
export class LocalizationPage {
  date = new Date(2000, 0, 1); // 01.01.2000
  datetime = new Date(2000, 0, 1, 12, 30); // 01.01.2000 12:30
  decimal = 213.12345;
  money = 100000.12345;
}

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
