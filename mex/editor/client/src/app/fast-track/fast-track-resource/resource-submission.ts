import { HttpClient } from "@angular/common/http";
import type { Signal } from "@angular/core";
import { inject, Injectable } from "@angular/core";
import { combineLatest, map, type Observable, switchMap } from "rxjs";

import type { CreateContactPoint, CreatePerson } from "../../shared/models/create-item";
import type { FastTrackResourceModel } from "./fast-track-resource.models";

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class ResourceSubmission {
  private http = inject(HttpClient);

  submit(model: Signal<FastTrackResourceModel>): Observable<{ stableTargetId: string }> {
    const resource = model();
    const contactIds: Observable<string>[] = [];

    return combineLatest(contactIds).pipe(
      switchMap((x) =>
        this.http.post<{ stableTargetId: string }>("api/v0/backend/rule-set", {
          additive: {
            // accessRestriction: resource.accessRestriction,
            contact: x,
            theme: resource.theme,
            title: resource.title,
            unitInCharge: resource.unitInCharge,
            entityType: "AdditiveResource",
          },
          entityType: "ResourceRuleSetRequest",
        }),
      ),
    );
  }

  submitContactPoint(element: CreateContactPoint): Observable<string> {
    return this.http
      .post<{ stableTargetId: string }>("api/v0/backend/rule-set", {
        additive: {
          email: element.email,
          entityType: "AdditiveContactPoint",
        },
        entityType: "ContactPointRuleSetRequest",
      })
      .pipe(map((x) => x.stableTargetId));
  }

  submitPerson(element: CreatePerson): Observable<string> {
    return this.http
      .post<{ stableTargetId: string }>("api/v0/backend/rule-set", {
        additive: {
          givenName: [element.givenName],
          familyName: [element.familyName],
          entityType: "AdditivePerson",
        },
        entityType: "PersonRuleSetRequest",
      })
      .pipe(map((x) => x.stableTargetId));
  }
}
