import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { TextEditor } from "./text-editor";

describe("TextEditor", () => {
  let component: TextEditor;
  let fixture: ComponentFixture<TextEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextEditor],
    }).compileComponents();

    fixture = TestBed.createComponent(TextEditor);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
