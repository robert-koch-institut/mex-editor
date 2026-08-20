import { HttpTestingController } from "@angular/common/http/testing";
import type { ComponentFixture } from "@angular/core/testing";
import { TestBed } from "@angular/core/testing";
import { MatDialog } from "@angular/material/dialog";
import { of } from "rxjs";

import { CreateItemDialog } from "../create-item-dialog/create-item-dialog";
import { ReferenceSelect } from "./reference-select";

// eslint-disable-next-line max-lines-per-function
describe("ReferenceSelect", () => {
  let fixture: ComponentFixture<ReferenceSelect>;
  let component: ReferenceSelect;
  let httpMock: HttpTestingController;
  let dialogOpenSpy: ReturnType<typeof vi.fn>;

  beforeEach(async () => {
    vi.useFakeTimers();
    dialogOpenSpy = vi.fn();

    await TestBed.configureTestingModule({
      imports: [ReferenceSelect],
      providers: [{ provide: MatDialog, useValue: { open: dialogOpenSpy } }],
    }).compileComponents();

    httpMock = TestBed.inject(HttpTestingController);
    fixture = TestBed.createComponent(ReferenceSelect);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("should create", () => {
    expect(component).toBeTruthy();
  });

  it("does not issue a search request while the query is empty", async () => {
    await vi.advanceTimersByTimeAsync(250);
    httpMock.expectNone(() => true);
  });

  it("searches with the debounced query and the (default) entity types", async () => {
    component["searchQuery"].set("jane");
    await vi.advanceTimersByTimeAsync(250);
    fixture.detectChanges();

    const req = httpMock.expectOne(
      (r) => r.url === "api/v0/backend/preview-item" && r.params.get("q") === "jane",
    );
    expect(req.request.params.getAll("entityType")).toEqual([
      "MergedPerson",
      "MergedContactPoint",
      "MergedOrganizationalUnit",
    ]);
    req.flush({ items: [], total: 0 });
  });

  it("restricts the search entity types to validEntityTypes when given", async () => {
    fixture.componentRef.setInput("validEntityTypes", ["Person"]);
    component["searchQuery"].set("jane");
    await vi.advanceTimersByTimeAsync(250);
    fixture.detectChanges();

    const req = httpMock.expectOne((r) => r.url === "api/v0/backend/preview-item");
    expect(req.request.params.getAll("entityType")).toEqual(["MergedPerson"]);
    req.flush({ items: [], total: 0 });
  });

  describe("addValue / removeValue", () => {
    it("adds an item to value", () => {
      const person = {
        $type: "PreviewPerson" as const,
        identifier: "person-1",
        fullName: ["Jane Doe"],
      };
      component["addValue"](person);
      expect(component.value()).toEqual([person]);
    });

    it("deduplicates by identifier when the same saved item is added twice", () => {
      const person = {
        $type: "PreviewPerson" as const,
        identifier: "person-1",
        fullName: ["Jane Doe"],
      };
      component["addValue"](person);
      component["addValue"](person);
      expect(component.value()).toEqual([person]);
    });

    it("does NOT deduplicate unsaved CreateItem drafts with identical content but different references", () => {
      const draftA = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
      const draftB = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
      component["addValue"](draftA);
      component["addValue"](draftB);
      expect(component.value().length).toBe(2);
    });

    it("removes a saved item by identifier", () => {
      const person = {
        $type: "PreviewPerson" as const,
        identifier: "person-1",
        fullName: ["Jane Doe"],
      };
      component["addValue"](person);
      component["removeValue"](person);
      expect(component.value()).toEqual([]);
    });

    it("removes an unsaved draft only by exact reference", () => {
      const draftA = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
      const draftB = { $type: "CreatePerson" as const, givenName: "Jane", familyName: "Doe" };
      component["addValue"](draftA);
      component["addValue"](draftB);

      component["removeValue"](draftA);

      expect(component.value()).toEqual([draftB]);
    });
  });

  describe("create-item dialog integration", () => {
    it("opens the dialog with the current search query and allowed types", () => {
      fixture.componentRef.setInput("validEntityTypes", ["Person"]);
      fixture.componentRef.setInput("isCreationEnabled", true);
      component["searchQuery"].set("jane");
      fixture.detectChanges();

      dialogOpenSpy.mockReturnValue({ afterClosed: () => of(null) });
      component["showCreateDialog"]();

      expect(dialogOpenSpy).toHaveBeenCalledWith(
        CreateItemDialog,
        expect.objectContaining({
          data: { inputText: "jane", allowedTypes: ["Person"] },
        }),
      );
    });

    it("adds the dialog's result to value when confirmed", () => {
      const created = { $type: "CreatePerson", givenName: "Jane", familyName: "Doe" };
      dialogOpenSpy.mockReturnValue({ afterClosed: () => of(created) });

      component["showCreateDialog"]();

      expect(component.value()).toEqual([created]);
    });

    it("adds nothing when the dialog is cancelled (closed with no result)", () => {
      dialogOpenSpy.mockReturnValue({ afterClosed: () => of(null) });

      component["showCreateDialog"]();

      expect(component.value()).toEqual([]);
    });
  });

  it("toggles an entity type in and out of the active search filter", () => {
    fixture.componentRef.setInput("validEntityTypes", ["Person", "ContactPoint"]);
    fixture.detectChanges();

    component["toggleSearchEntityType"]("Person");
    expect(component["searchEntityTypes"]()).toEqual(expect.not.arrayContaining(["Person"]));

    component["toggleSearchEntityType"]("Person");
    expect(component["searchEntityTypes"]()).toEqual(expect.arrayContaining(["Person"]));
  });
});
