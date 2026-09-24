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
});
