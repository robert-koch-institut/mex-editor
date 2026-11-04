import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { LinkLanguageMenu } from "./link-language-menu";

describe("LanguageMenu", () => {
  let component: LinkLanguageMenu;
  let fixture: ComponentFixture<LinkLanguageMenu>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LinkLanguageMenu],
    }).compileComponents();

    fixture = TestBed.createComponent(LinkLanguageMenu);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });
});
