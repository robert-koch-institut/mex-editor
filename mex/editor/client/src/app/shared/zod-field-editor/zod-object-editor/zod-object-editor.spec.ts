import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ZodObjectEditor } from "./zod-object-editor";

describe("ZodObjectEditor", () => {
  let component: ZodObjectEditor<never>;
  let fixture: ComponentFixture<ZodObjectEditor<never>>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZodObjectEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(ZodObjectEditor<never>);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
