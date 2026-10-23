import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { TranslocoService } from "@jsverse/transloco";
import {
  catchError,
  combineLatest,
  firstValueFrom,
  map,
  type Observable,
  of,
  switchMap,
  take,
  throwError,
} from "rxjs";

import type { PreviewItem } from "../../shared/models";
import type { CreateItem } from "../../shared/models/create-item";
import {
  type CreateContactPoint,
  type CreatePerson,
  isCreateItem,
} from "../../shared/models/create-item";
import type { ContactPointRuleSetRequest } from "../../shared/models/generated/contact-point";
import type { PersonRuleSetRequest } from "../../shared/models/generated/person";
import type {
  AdditiveResource,
  ResourceRuleSetRequest,
  ResourceRuleSetResponse,
} from "../../shared/models/generated/resource";
import {
  type FastTrackResourceModel,
  type FastTrackResourceSubmissionResult,
  FastTrackResourceSubPostError,
} from "./fast-track-resource.models";

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class FastTrackResourceSubmission {
  private http = inject(HttpClient);
  private transloco = inject(TranslocoService);

  async submit(model: FastTrackResourceModel): Promise<FastTrackResourceSubmissionResult> {
    let language: "de" | "en" = "de";
    const currentLanguage = this.transloco.getActiveLang();
    if (this.isValidLanguage(currentLanguage)) {
      language = currentLanguage;
    }

    const submitter = (x: CreateItem | PreviewItem) =>
      isCreateItem(x) ? this.submitCreateItem(x) : of(x.identifier);

    const contactIds = model.contact.map(submitter);
    const contribIds = model.contributor.map(submitter);
    const unitInChargeIds = model.unitInCharge.map(submitter);
    const creatorIds = model.creator.map(submitter);
    const contributingUnitIds = model.contributingUnit.map(submitter);

    const combiner = (ids: Observable<string>[]) => (ids.length > 0 ? combineLatest(ids) : of([]));

    const saveRequest = combineLatest([
      combiner(contactIds),
      combiner(contribIds),
      combiner(unitInChargeIds),
      combiner(creatorIds),
      combiner(contributingUnitIds),
    ]).pipe(
      take(1),
      switchMap(([contact, contributor, unitInCharge, creator, contributingUnit]) => {
        const additive = this.mapModel(
          model,
          { contact, contributor, unitInCharge, creator, contributingUnit },
          language,
        );

        const payload: ResourceRuleSetRequest = {
          $type: "ResourceRuleSetRequest",
          additive,
        };

        return this.http
          .post<ResourceRuleSetResponse>("api/v0/backend/rule-set", payload)
          .pipe(
            catchError((err: Error) => of({ $type: "PostError" as const, error: err, payload })),
          );
      }),
    );

    const response = await firstValueFrom(saveRequest);
    if (response.$type == "ResourceRuleSetResponse") {
      return { success: true, response };
    }
    return { success: false, payload: response.payload, error: response.error };
  }

  private isValidLanguage(value: string): value is "en" | "de" {
    return ["en", "de"].includes(value);
  }

  private mapModel(
    model: FastTrackResourceModel,
    resolvedRefs: {
      contact: string[];
      contributor: string[];
      unitInCharge: string[];
      creator: string[];
      contributingUnit: string[];
    },
    language: "en" | "de",
  ): AdditiveResource {
    const stringToText = (x: string) => ({ value: x, language });
    return {
      $type: "AdditiveResource",
      contact: resolvedRefs.contact,
      contributor: resolvedRefs.contributor,
      unitInCharge: resolvedRefs.unitInCharge,
      creator: resolvedRefs.creator,
      contributingUnit: resolvedRefs.contributingUnit,
      rights: [stringToText(model.rights)],
      title: [stringToText(model.title)],
      description: [stringToText(model.description)],
      accrualPeriodicity: model.accrualPeriodicity,
      theme: model.theme,
      end: model.end ? [model.end.toISODate()!] : undefined,
      start: model.start ? [model.start.toISODate()!] : undefined,
      hasLegalBasis: [stringToText(model.hasLegalBasis)],
      keyword: [
        ...model.keywords.de.map((x) => ({ value: x, language: "de" as const })),
        ...model.keywords.en.map((x) => ({ value: x, language: "en" as const })),
      ],
      provenance: [stringToText(model.provenance)],
      resourceCreationMethod: model.resourceCreationMethod,
      resourceTypeGeneral: model.resourceTypeGeneral,
      spatial: [stringToText(model.spatial)],
    };
  }

  private mapCreateItem(item: CreateItem): PersonRuleSetRequest | ContactPointRuleSetRequest {
    if (item.$type == "CreateContactPoint") {
      return this.mapCreateContactPoint(item);
    }
    return this.mapCreatePerson(item);
  }

  private mapCreatePerson(item: CreatePerson) {
    return {
      additive: {
        givenName: [item.givenName],
        familyName: [item.familyName],
        $type: "AdditivePerson" as const,
      },
      $type: "PersonRuleSetRequest" as const,
    };
  }

  private mapCreateContactPoint(item: CreateContactPoint) {
    return {
      additive: {
        email: [item.email],
        $type: "AdditiveContactPoint" as const,
      },
      $type: "ContactPointRuleSetRequest" as const,
    };
  }

  private submitCreateItem(item: CreateItem): Observable<string> {
    const payload = this.mapCreateItem(item);
    return this.http.post<{ stableTargetId?: string }>("api/v0/backend/rule-set", payload).pipe(
      map((x) => {
        if (x.stableTargetId) return x.stableTargetId;
        throw new Error("No stableTargetId in response.");
      }),
      catchError((err) => throwError(() => new FastTrackResourceSubPostError(err, payload))),
    );
  }
}
