import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { Edit } from "./edit";

describe("Edit", () => {
  let component: Edit;
  let fixture: ComponentFixture<Edit>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Edit],
    }).compileComponents();

    fixture = TestBed.createComponent(Edit);
    component = fixture.componentInstance;
    fixture.componentRef.setInput("entityId", "12345");
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
