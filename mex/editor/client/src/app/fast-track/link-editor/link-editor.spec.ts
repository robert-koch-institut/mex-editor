import { ComponentFixture, TestBed } from "@angular/core/testing";

import { LinkEditor } from "./link-editor";

describe("LinkEditor", () => {
  let component: LinkEditor;
  let fixture: ComponentFixture<LinkEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LinkEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(LinkEditor);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
