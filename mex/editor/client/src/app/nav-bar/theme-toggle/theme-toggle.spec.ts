import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";

import { ThemeToggle } from "./theme-toggle";

describe("ThemeToggleComponent", () => {
  let component: ThemeToggle;
  let fixture: ComponentFixture<ThemeToggle>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ThemeToggle],
    }).compileComponents();

    fixture = TestBed.createComponent(ThemeToggle);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("should toggle theme component value", () => {
    const initialMode = component.isDarkMode();
    component.toggleTheme();
    expect(component.isDarkMode()).toBe(!initialMode);
  });

  it("should add 'dark-mode' class on html element when in dark mode; otherwise NULL", () => {
    const htmlElement = document.documentElement;

    const initial = component.isDarkMode();
    if (component.isDarkMode()) expect(htmlElement.classList).toContain("dark-mode");
    else expect(htmlElement.classList).not.toContain("dark-mode");

    component.toggleTheme();
    expect(component.isDarkMode()).toBe(!initial);

    if (component.isDarkMode()) expect(htmlElement.classList).toContain("dark-mode");
    else expect(htmlElement.classList).not.toContain("dark-mode");
  });
});
