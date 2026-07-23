import { HttpClient } from "@angular/common/http";
import type { Signal } from "@angular/core";
import { inject, Injectable } from "@angular/core";
import { combineLatest, map, of, switchMap, type Observable } from "rxjs";

import type { FastTrackResourceModel } from "./fast-track-resource.types";
import type { CreateMail, CreatePerson } from "./create-contact";

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class ResourceSubmission {
  private http = inject(HttpClient);

  submit(model: Signal<FastTrackResourceModel>): Observable<{ stableTargetId: string }> {
    const resource = model();
    const contactIds: Observable<string>[] = [];

    for (const element of resource.contacts) {
      if (typeof element == "string") continue;
      if ("$createtype" in element) {
        if (element.$createtype == "mail") {
          contactIds.push(this.submitContactPoint(element));
        } else {
          contactIds.push(this.submitPerson(element));
        }
      } else {
        contactIds.push(of(element.id));
      }
    }

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

  submitContactPoint(element: CreateMail): Observable<string> {
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
          givenName: [element.firstname],
          familyName: [element.lastname],
          entityType: "AdditivePerson",
        },
        entityType: "PersonRuleSetRequest",
      })
      .pipe(map((x) => x.stableTargetId));
  }
}
