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

import { asTextLanguage, type PreviewItem } from "../../shared/models";
import type { CreateItem, CreateOrganization } from "../../shared/models/create-item";
import {
  type CreateContactPoint,
  type CreatePerson,
  isCreateItem,
} from "../../shared/models/create-item";
import {
  type ContactPointRuleSetRequest,
  ContactPointRuleSetRequestSchema,
} from "../../shared/models/generated/contact-point";
import type {
  AdditiveOrganization,
  OrganizationRuleSetRequest,
} from "../../shared/models/generated/organization";
import { OrganizationRuleSetRequestSchema } from "../../shared/models/generated/organization";
import {
  type PersonRuleSetRequest,
  PersonRuleSetRequestSchema,
} from "../../shared/models/generated/person";
import {
  type AdditiveResource,
  AdditiveResourceSchema,
  ResourceRuleSetRequestSchema,
  type ResourceRuleSetResponse,
} from "../../shared/models/generated/resource";
import type { TextLanguage } from "../../shared/models/generated/shared";
import { TextSchema } from "../../shared/models/generated/shared";
import { SubmissionError, type SubmissionResult } from "../../shared/models/submission-result";
import { type FastTrackResourceModel } from "./fast-track-resource.models";

@Injectable({ providedIn: "root" })
/**
 * Service to submit FastTrackResourceModels.
 */
export class FastTrackResourceSubmission {
  private http = inject(HttpClient);
  private transloco = inject(TranslocoService);

  async submit(model: FastTrackResourceModel): Promise<SubmissionResult<ResourceRuleSetResponse>> {
    const currentLanguage = this.transloco.getActiveLang();
    const language = asTextLanguage(currentLanguage);

    try {
      const submitter = (x: CreateItem | PreviewItem) =>
        isCreateItem(x) ? this.submitCreateItem(x, language) : of(x.identifier);

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

          const payload = ResourceRuleSetRequestSchema.parse({
            $type: "ResourceRuleSetRequest",
            additive,
          });

          return this.http
            .post<ResourceRuleSetResponse>("api/v0/backend/rule-set", payload)
            .pipe(catchError((err: Error) => throwError(() => new SubmissionError(payload, err))));
        }),
      );

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

  private mapModel(
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
    const stringToText = (value: string) => TextSchema.parse({ value, language });
    const isValidTextString = (x: string) => x && x.length >= 1;
    const mapped: AdditiveResource = {
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
      end: model.end ? [model.end] : [],
      start: model.start ? [model.start] : [],
      hasLegalBasis: isValidTextString(model.hasLegalBasis)
        ? [stringToText(model.hasLegalBasis)]
        : [],
      keyword: [
        ...model.keywords.de.map((x) => ({ value: x, language: "de" as const })),
        ...model.keywords.en.map((x) => ({ value: x, language: "en" as const })),
      ],
      provenance: [stringToText(model.provenance)],
      resourceCreationMethod: model.resourceCreationMethod,
      spatial: isValidTextString(model.spatial) ? [stringToText(model.spatial)] : [],
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
}
