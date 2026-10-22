import { ComponentFixture, TestBed } from "@angular/core/testing";

import { ZodArrayEditor } from "./zod-array-editor";

describe("ZodArrayEditor", () => {
  let component: ZodArrayEditor;
  let fixture: ComponentFixture<ZodArrayEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZodArrayEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(ZodArrayEditor);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
