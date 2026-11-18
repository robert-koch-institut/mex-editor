import { ComponentFixture, TestBed } from "@angular/core/testing";
import { TestGenericZodControl } from "./test-generic-zod-control";

describe("TestGenericZodControl", () => {
  let component: TestGenericZodControl;
  let fixture: ComponentFixture<TestGenericZodControl>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestGenericZodControl],
    }).compileComponents();

    fixture = TestBed.createComponent(TestGenericZodControl);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
