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
import {
  type ContactPointRuleSetRequest,
  ContactPointRuleSetRequestSchema,
} from "../../shared/models/generated/contact-point";
import {
  type PersonRuleSetRequest,
  PersonRuleSetRequestSchema,
} from "../../shared/models/generated/person";
import {
  type AdditiveResource,
  AdditiveResourceSchema,
  type ResourceRuleSetRequest,
  type ResourceRuleSetResponse,
} from "../../shared/models/generated/resource";
import { TextSchema } from "../../shared/models/generated/shared";
import type { SubmissionResult } from "../../shared/models/submission-result";
import { type FastTrackResourceModel } from "./fast-track-resource.models";

/**
 * Class for Error during submission of items including its payload.
 */
export class SubmissionError<T extends { $type: string }> extends Error {
  constructor(
    readonly payload: T,
    readonly innerError?: Error,
  ) {
    super(`Error while submitting '${payload.$type}'`);
  }
}

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class FastTrackResourceSubmission {
  private http = inject(HttpClient);
  private transloco = inject(TranslocoService);

  async submit(model: FastTrackResourceModel): Promise<SubmissionResult<ResourceRuleSetResponse>> {
    let language: "de" | "en" = "de";
    const currentLanguage = this.transloco.getActiveLang();
    if (this.isValidLanguage(currentLanguage)) {
      language = currentLanguage;
    }

    const submitter = (x: CreateItem | PreviewItem) =>
      isCreateItem(x) ? this.submitCreateItem(x) : of(x.identifier);

    const contactIds = model.contact.map(submitter);
    const contributorIds = model.contributor.map(submitter);
    const unitInChargeIds = model.unitInCharge.map(submitter);
    const creatorIds = model.creator.map(submitter);
    const contributingUnitIds = model.contributingUnit.map(submitter);

    const combiner = <T>(ids: Observable<T>[]) => (ids.length > 0 ? combineLatest(ids) : of([]));

    const saveRequest = combineLatest([
      combiner(contactIds),
      combiner(contributorIds),
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
          .pipe(catchError((err: Error) => throwError(() => new SubmissionError(payload, err))));
      }),
    );

    try {
      const response = await firstValueFrom(saveRequest);
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
    const stringToText = (x: string) => TextSchema.parse({ value: x, language });
    return AdditiveResourceSchema.parse({
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
    });
  }

  private mapCreateItem(item: CreateItem): PersonRuleSetRequest | ContactPointRuleSetRequest {
    if (item.$type == "CreateContactPoint") {
      return this.mapCreateContactPoint(item);
    }
    return this.mapCreatePerson(item);
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

  private submitCreateItem(item: CreateItem) {
    const payload = this.mapCreateItem(item);
    return this.http.post<{ stableTargetId?: string }>("api/v0/backend/rule-set", payload).pipe(
      map((x) => {
        if (x.stableTargetId) return x.stableTargetId;
        throw new Error("No stableTargetId in response.", { cause: x });
      }),
      catchError((err) => throwError(() => new SubmissionError(payload, err))),
    );
  }
}
