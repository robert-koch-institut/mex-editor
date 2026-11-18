import { ComponentFixture, TestBed } from "@angular/core/testing";
import { ZodObjectEditor } from "./zod-object-editor";

describe("ZodObjectEditor", () => {
  let component: ZodObjectEditor;
  let fixture: ComponentFixture<ZodObjectEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZodObjectEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(ZodObjectEditor);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
