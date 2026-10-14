import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ToastContent } from "./toast-content";

describe("ToastContent", () => {
  let component: ToastContent;
  let fixture: ComponentFixture<ToastContent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ToastContent],
    }).compileComponents();

    fixture = TestBed.createComponent(ToastContent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
