import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { CreateItemDialog } from "./create-item-dialog";

describe("CreateItemDialog", () => {
  let component: CreateItemDialog;
  let fixture: ComponentFixture<CreateItemDialog>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateItemDialog],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateItemDialog);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
