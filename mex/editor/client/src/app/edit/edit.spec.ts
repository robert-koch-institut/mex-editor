import { HttpTestingController } from "@angular/common/http/testing";
import { TestBed } from "@angular/core/testing";

import { Edit } from "./edit";
describe("Edit", () => {
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Edit],
      // providers: [provideHttpClientTesting()],
    }).compileComponents();

    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpTesting.verify();
  });

  it("should create the component and use the default entity value", async () => {
    const fixture = TestBed.createComponent(Edit);

    fixture.componentRef.setInput("entityId", "rule-123");
    fixture.detectChanges();

    // Flush Angular's scheduled effects, including httpResource.
    TestBed.tick();

    expect(fixture.componentInstance).toBeTruthy();

    expect(fixture.componentInstance.entity.value()).toEqual({
      stableTargetId: "NONE",
    });

    const request = httpTesting.expectOne("api/v0/backend/rule-set/rule-123");

    expect(request.request.method).toBe("GET");

    request.flush({ stableTargetId: "target-456" });

    TestBed.tick();
    await fixture.whenStable();

    expect(fixture.componentInstance.entity.value()).toEqual({
      stableTargetId: "target-456",
    });

    fixture.destroy();
  });

  it("should request the entity for the supplied entityId", async () => {
    const fixture = TestBed.createComponent(Edit);

    fixture.componentRef.setInput("entityId", "another-rule");
    fixture.detectChanges();
    TestBed.tick();

    const request = httpTesting.expectOne("api/v0/backend/rule-set/another-rule");

    expect(request.request.method).toBe("GET");

    request.flush({ stableTargetId: "another-target" });

    TestBed.tick();
    await fixture.whenStable();

    expect(fixture.componentInstance.entity.value()).toEqual({
      stableTargetId: "another-target",
    });

    fixture.destroy();
  });
});
