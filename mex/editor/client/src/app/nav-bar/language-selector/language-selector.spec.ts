import type { ComponentFixture} from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LanguageSelector } from "./language-selector";

describe("LanguageSelectorComponent", () => {
  let component: LanguageSelector;
  let fixture: ComponentFixture<LanguageSelector>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LanguageSelector],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelector);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
