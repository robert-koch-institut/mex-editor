import { HttpClient } from "@angular/common/http";
import { inject, Injectable } from "@angular/core";
import { TranslocoService } from "@jsverse/transloco";
import { combineLatest, firstValueFrom, map, type Observable, of, switchMap, take } from "rxjs";

import type { PreviewItem } from "../../shared/models";
import type { CreateItem } from "../../shared/models/create-item";
import {
  type CreateContactPoint,
  type CreatePerson,
  isCreateItem,
} from "../../shared/models/create-item";
import type {
  ResourceRuleSetRequest,
  ResourceRuleSetResponse,
} from "../../shared/models/generated/resource";
import { type AdditiveResource } from "../../shared/models/generated/resource";
import type { FastTrackResourceModel } from "./fast-track-resource.models";

function combineIdsOrEmpty(ids: Observable<string>[]): Observable<string[]> {
  return ids.length > 0 ? combineLatest(ids) : of([]);
}

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class FastTrackResourceSubmission {
  private http = inject(HttpClient);
  private transloco = inject(TranslocoService);

  mapModel(
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

  private isValidLanguage(value: string): value is "en" | "de" {
    return value in ["en", "de"];
  }

  async submit(model: FastTrackResourceModel) {
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

    const saveRequest = combineLatest([
      combineIdsOrEmpty(contactIds),
      combineIdsOrEmpty(contribIds),
      combineIdsOrEmpty(unitInChargeIds),
      combineIdsOrEmpty(creatorIds),
      combineIdsOrEmpty(contributingUnitIds),
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

        return this.http.post<ResourceRuleSetResponse>("api/v0/backend/rule-set", payload);
      }),
    );

    try {
      return await firstValueFrom(saveRequest);
    } catch (err) {
      return { kind: "serverError", message: "Failed to save rule set", error: err };
    }
  }

  private submitCreateItem(item: CreateItem): Observable<string> {
    if (item.$type == "CreateContactPoint") return this.submitContactPoint(item);
    return this.submitPerson(item);
  }

  private submitContactPoint(element: CreateContactPoint): Observable<string> {
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

  private submitPerson(element: CreatePerson): Observable<string> {
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
