import { ComponentFixture, TestBed } from "@angular/core/testing";

import { ZodFieldEditor } from "./zod-field-editor";

describe("ZodFieldEditor", () => {
  let component: ZodFieldEditor;
  let fixture: ComponentFixture<ZodFieldEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZodFieldEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(ZodFieldEditor);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
