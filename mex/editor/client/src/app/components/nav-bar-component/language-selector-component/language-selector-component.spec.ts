import type { ComponentFixture} from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LanguageSelectorComponent } from "./language-selector-component";

describe("LanguageSelectorComponent", () => {
  let component: LanguageSelectorComponent;
  let fixture: ComponentFixture<LanguageSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LanguageSelectorComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LanguageSelectorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
