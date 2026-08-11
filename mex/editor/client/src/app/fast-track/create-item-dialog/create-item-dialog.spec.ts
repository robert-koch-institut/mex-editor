import { TestBed } from "@angular/core/testing";
import type { CreateItemDialogData } from "./create-item-dialog";
import { CreateItemDialog } from "./create-item-dialog";
import { Component, input, model } from "@angular/core";
import { MAT_DIALOG_DATA, MatDialogRef } from "@angular/material/dialog";
import { CreateContactPointForm } from "./create-contact-point-form/create-contact-point-form";
import { CreatePersonForm } from "./create-person-form/create-person-form";
import { By } from "@angular/platform-browser";

@Component({ selector: "mex-create-person-form", standalone: true, template: `` })
class FakeCreatePersonForm {
  inputText = input<string>();
  data = model<unknown>();
  isValid = model<boolean>(false);
}

@Component({ selector: "mex-create-contact-point-form", standalone: true, template: `` })
class FakeCreateContactPointForm {
  inputText = input<string>();
  data = model<unknown>();
  isValid = model<boolean>(false);
}

function setup(data: CreateItemDialogData) {
  const closeSpy = vi.fn();

  TestBed.configureTestingModule({
    imports: [CreateItemDialog],
    providers: [
      { provide: MAT_DIALOG_DATA, useValue: data },
      { provide: MatDialogRef, useValue: { close: closeSpy } },
    ],
  });
  TestBed.overrideComponent(CreateItemDialog, {
    remove: { imports: [CreatePersonForm, CreateContactPointForm] },
    add: { imports: [FakeCreatePersonForm, FakeCreateContactPointForm] },
  });

  const fixture = TestBed.createComponent(CreateItemDialog);
  fixture.detectChanges();
  return { fixture, closeSpy, component: fixture.componentInstance };
}

describe("CreateItemDialog", () => {
  it("should create", () => {
    const { component } = setup({});
    expect(component).toBeTruthy();
  });

  it("shows both tabs by default", () => {
    const { component } = setup({});
    expect(component.tabs().map((t) => t.$type)).toEqual(["Person", "ContactPoint"]);
  });

  it("hides the tab header if there is only one allowed type", () => {
    const { component, fixture } = setup({ allowedTypes: ["Person"] });
    expect(component.tabs().length).toEqual(1);
    fixture.debugElement.queryAll(By.css(".mat-tab-header")).forEach((header) => {
      header.nativeElement.style.display = "none";
    });
  });

  it("restricts the tabs to allowedTypes when provided", () => {
    const { component } = setup({ allowedTypes: ["Person"] });
    expect(component.tabs().map((t) => t.$type)).toEqual(["Person"]);
  });

  it("starts on Person by default", () => {
    const { component } = setup({});
    expect(component.tabs()[component.selectedTabIndex()].$type).toBe("Person");
  });

  it("starts on the given initialSelectedTab", () => {
    const { component } = setup({ initialSelectedTab: "ContactPoint" });
    expect(component.tabs()[component.selectedTabIndex()].$type).toBe("ContactPoint");
  });

  it("disables the save button while the active tab's data is invalid", () => {
    const { fixture } = setup({});
    const saveButton = fixture.debugElement.queryAll(By.css("button"))[1]
      .nativeElement as HTMLButtonElement;
    expect(saveButton.disabled).toBe(true);
  });

  it("enables the save button once the active tab's data becomes valid", () => {
    const { fixture, component } = setup({});
    component.tabs.update((tabs) => {
      return tabs.map((t) => {
        if (t.$type === "Person") {
          return {
            ...t,
            isValid: true,
            data: { $type: "CreatePerson", givenName: "Jane", familyName: "Doe" },
          };
        }
        return t;
      });
    });
    fixture.detectChanges();

    const saveButton = fixture.debugElement.queryAll(By.css("button"))[1]
      .nativeElement as HTMLButtonElement;
    expect(saveButton.disabled).toBe(false);
  });

  it("does not close on Enter while the active tab is invalid", () => {
    const { fixture, closeSpy } = setup({});
    fixture.nativeElement.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Enter", bubbles: true }),
    );
    expect(closeSpy).not.toHaveBeenCalled();
  });

  it("closes with the active tab's data on Enter once it's valid", () => {
    const { fixture, component, closeSpy } = setup({});
    const personData = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
    component.tabs.update((tabs) => {
      return tabs.map((t) => {
        if (t.$type === "Person") {
          return {
            ...t,
            isValid: true,
            data: personData,
          };
        }
        return t;
      });
    });
    fixture.detectChanges();

    fixture.nativeElement.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Enter", bubbles: true }),
    );

    expect(closeSpy).toHaveBeenCalledWith(personData);
  });

  it("closes with the currently SELECTED tab's data, not another valid tab's", () => {
    const { fixture, component, closeSpy } = setup({});
    component.personTab.isValid = true;
    component.personTab.data = { $type: "CreatePerson", givenName: "Jane", familyName: "Doe" };

    const contactData = { $type: "CreateContactPoint" as const, email: "jane.doe@example.org" };
    component.contactPointTab.isValid = true;
    component.contactPointTab.data = contactData;

    component.selectedTabIndex.set(1); // switch to ContactPoint
    fixture.detectChanges();

    fixture.nativeElement.dispatchEvent(
      new KeyboardEvent("keydown", { key: "Enter", bubbles: true }),
    );

    expect(closeSpy).toHaveBeenCalledWith(contactData);
  });
});
