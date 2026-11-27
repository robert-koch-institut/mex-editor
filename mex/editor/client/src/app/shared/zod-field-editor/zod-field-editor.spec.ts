import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ZodFieldEditor } from "./zod-field-editor";

describe("ZodFieldEditor", () => {
  let component: ZodFieldEditor<never>;
  let fixture: ComponentFixture<ZodFieldEditor<never>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZodFieldEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(ZodFieldEditor<never>);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
