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

import { asTextLanguage, type PreviewItem } from "../shared/models";
import type { CreateItem, CreateOrganization } from "../shared/models/create-item";
import {
  type CreateContactPoint,
  type CreatePerson,
  isCreateItem,
} from "../shared/models/create-item";
import type {
  ActivityRuleSetResponse,
  AdditiveActivity,
} from "../shared/models/generated/activity";
import {
  ActivityRuleSetRequestSchema,
  AdditiveActivitySchema,
} from "../shared/models/generated/activity";
import {
  type ContactPointRuleSetRequest,
  ContactPointRuleSetRequestSchema,
} from "../shared/models/generated/contact-point";
import type {
  AdditiveOrganization,
  OrganizationRuleSetRequest,
} from "../shared/models/generated/organization";
import { OrganizationRuleSetRequestSchema } from "../shared/models/generated/organization";
import {
  type PersonRuleSetRequest,
  PersonRuleSetRequestSchema,
} from "../shared/models/generated/person";
import {
  type AdditiveResource,
  AdditiveResourceSchema,
  ResourceRuleSetRequestSchema,
  type ResourceRuleSetResponse,
} from "../shared/models/generated/resource";
import type { Text, TextLanguage } from "../shared/models/generated/shared";
import { TextSchema } from "../shared/models/generated/shared";
import { SubmissionError, type SubmissionResult } from "../shared/models/submission-result";
import type { FastTrackActivityModel } from "./fast-track-activity.model";
import { type FastTrackResourceModel } from "./fast-track-resource.models";

function stringToText(value: string, language: TextLanguage): Text {
  return TextSchema.parse({ value, language });
}

function isValidTextString(value: string) {
  return TextSchema.safeParse({ value }).success;
}

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class FastTrackSubmission {
  private http = inject(HttpClient);
  private transloco = inject(TranslocoService);

  async submit(
    model: FastTrackResourceModel | FastTrackActivityModel,
  ): Promise<SubmissionResult<ResourceRuleSetResponse | ActivityRuleSetResponse>> {
    const currentLanguage = this.transloco.getActiveLang();
    const language = asTextLanguage(currentLanguage);

    try {
      const submitRequest =
        model.$type === "FastTrackResourceModel"
          ? firstValueFrom(this.buildResourceSubmitRequest(model, language))
          : firstValueFrom(this.buildActivitySubmitRequest(model, language));

      const response = await submitRequest;
      return { success: true, response: response };
    } catch (error: unknown) {
      return {
        success: false,
        error:
          error instanceof Error
            ? error
            : new Error("Unknwon Error while submitting 'FastTrackResource'.", { cause: model }),
      };
    }
  }

  private buildActivitySubmitRequest(
    model: FastTrackActivityModel,
    language: TextLanguage,
  ): Observable<ActivityRuleSetResponse> {
    return this.buildSubitemSubmitRequests(
      {
        contact: model.contact,
        responsibleUnit: model.responsibleUnit,
        involvedPerson: model.involvedPerson,
        involvedUnit: model.involvedUnit,
        funderOrCommissioner: model.funderOrCommissioner,
      },
      language,
    ).pipe(
      switchMap((subItems) => {
        const additive = this.mapActivityModel(model, subItems, language);
        const payload = ActivityRuleSetRequestSchema.parse({
          $type: "ActivityRuleSetRequest",
          additive,
        });

        return this.http
          .post<ActivityRuleSetResponse>("api/v0/backend/rule-set", payload)
          .pipe(catchError((err: Error) => throwError(() => new SubmissionError(payload, err))));
      }),
    );
  }

  private buildResourceSubmitRequest(
    model: FastTrackResourceModel,
    language: TextLanguage,
  ): Observable<ResourceRuleSetResponse> {
    return this.buildSubitemSubmitRequests(
      {
        contact: model.contact,
        contributor: model.contributor,
        unitInCharge: model.unitInCharge,
        creator: model.creator,
        contributingUnit: model.contributingUnit,
      },
      language,
    ).pipe(
      switchMap((subItems) => {
        const additive = this.mapResourceModel(model, subItems, language);
        const payload = ResourceRuleSetRequestSchema.parse({
          $type: "ResourceRuleSetRequest",
          additive,
        });

        return this.http
          .post<ResourceRuleSetResponse>("api/v0/backend/rule-set", payload)
          .pipe(catchError((err: Error) => throwError(() => new SubmissionError(payload, err))));
      }),
    );
  }

  private buildSubitemSubmitRequests<T extends Record<string, (CreateItem | PreviewItem)[]>>(
    sourcesObject: T,
    language: TextLanguage,
  ) {
    const submitter = (item: CreateItem | PreviewItem) =>
      isCreateItem(item) ? this.submitCreateItem(item, language) : of(item.identifier);
    const combiner = <S>(ids: Observable<S>[]) => (ids.length > 0 ? combineLatest(ids) : of([]));
    const observables = Object.fromEntries(
      Object.entries(sourcesObject).map(([key, items]) => [key, combiner(items.map(submitter))]),
    ) as { [K in keyof T]: Observable<string[]> };
    return combineLatest(observables).pipe(take(1));
  }

  private submitCreateItem(item: CreateItem, language: TextLanguage): Observable<string> {
    return of(this.mapCreateItem(item, language)).pipe(
      switchMap((payload) =>
        this.http.post<{ stableTargetId?: string }>("api/v0/backend/rule-set", payload).pipe(
          map((x) => {
            if (x.stableTargetId) return x.stableTargetId;
            throw new Error("No stableTargetId in response.", { cause: x });
          }),
          catchError((err) => throwError(() => new SubmissionError(payload, err))),
        ),
      ),
    );
  }

  private mapActivityModel(
    model: FastTrackActivityModel,
    resolvedRefs: {
      contact: string[];
      responsibleUnit: string[];
      involvedPerson: string[];
      involvedUnit: string[];
      funderOrCommissioner: string[];
    },
    language: TextLanguage,
  ): AdditiveActivity {
    const mapped: AdditiveActivity = {
      $type: "AdditiveActivity",

      contact: resolvedRefs.contact,
      responsibleUnit: resolvedRefs.responsibleUnit,
      involvedPerson: resolvedRefs.involvedPerson,
      involvedUnit: resolvedRefs.involvedUnit,
      funderOrCommissioner: resolvedRefs.funderOrCommissioner,

      title: [stringToText(model.title, language)],
      abstract: [stringToText(model.abstract, language)],
      shortName: isValidTextString(model.shortName)
        ? [stringToText(model.shortName, language)]
        : [],
      start: model.start ? [model.start] : [],
      end: model.end ? [model.end] : [],
      website: structuredClone(model.website),
      activityType: model.activityType,
    };
    return AdditiveActivitySchema.parse(mapped);
  }

  private mapResourceModel(
    model: FastTrackResourceModel,
    resolvedRefs: {
      contact: string[];
      contributor: string[];
      unitInCharge: string[];
      creator: string[];
      contributingUnit: string[];
    },
    language: TextLanguage,
  ): AdditiveResource {
    const mapped: AdditiveResource = {
      $type: "AdditiveResource",

      contact: resolvedRefs.contact,
      contributor: resolvedRefs.contributor,
      unitInCharge: resolvedRefs.unitInCharge,
      creator: resolvedRefs.creator,
      contributingUnit: resolvedRefs.contributingUnit,

      rights: [stringToText(model.rights, language)],
      title: [stringToText(model.title, language)],
      description: [stringToText(model.description, language)],
      accrualPeriodicity: model.accrualPeriodicity,
      theme: model.theme,
      end: model.end ? [model.end] : [],
      start: model.start ? [model.start] : [],
      hasLegalBasis: isValidTextString(model.hasLegalBasis)
        ? [stringToText(model.hasLegalBasis, language)]
        : [],
      keyword: [
        ...model.keywords.de.map((x) => ({ value: x, language: "de" as const })),
        ...model.keywords.en.map((x) => ({ value: x, language: "en" as const })),
      ],
      provenance: [stringToText(model.provenance, language)],
      resourceCreationMethod: model.resourceCreationMethod,
      spatial: isValidTextString(model.spatial) ? [stringToText(model.spatial, language)] : [],
    };
    return AdditiveResourceSchema.parse(mapped);
  }

  private mapCreateItem(
    item: CreateItem,
    language: TextLanguage,
  ): PersonRuleSetRequest | ContactPointRuleSetRequest | OrganizationRuleSetRequest {
    if (item.$type == "CreateContactPoint") {
      return this.mapCreateContactPoint(item);
    }
    if (item.$type == "CreateOrganization") {
      return this.mapCreateOrganization(item, language);
    }
    return this.mapCreatePerson(item);
  }

  private mapCreateOrganization(item: CreateOrganization, language: TextLanguage) {
    const additive: AdditiveOrganization = {
      $type: "AdditiveOrganization" as const,
      officialName: [TextSchema.parse({ value: item.officialName, language })],
    };
    return OrganizationRuleSetRequestSchema.parse({
      additive,
      $type: "PersonRuleSetRequest" as const,
    });
  }

  private mapCreatePerson(item: CreatePerson) {
    return PersonRuleSetRequestSchema.parse({
      additive: {
        givenName: [item.givenName],
        familyName: [item.familyName],
        $type: "AdditivePerson" as const,
      },
      $type: "PersonRuleSetRequest" as const,
    });
  }

  private mapCreateContactPoint(item: CreateContactPoint) {
    return ContactPointRuleSetRequestSchema.parse({
      additive: {
        email: [item.email],
        $type: "AdditiveContactPoint" as const,
      },
      $type: "ContactPointRuleSetRequest" as const,
    });
  }
}
