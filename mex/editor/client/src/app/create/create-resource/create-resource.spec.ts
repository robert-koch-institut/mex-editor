import { ComponentFixture, TestBed } from "@angular/core/testing";
import { CreateResource } from "./create-resource";

describe("CreateResource", () => {
  let component: CreateResource;
  let fixture: ComponentFixture<CreateResource>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateResource],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateResource);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
