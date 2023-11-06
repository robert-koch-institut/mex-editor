import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { JSONSchema7 } from 'json-schema';
import { Observable, map, shareReplay } from 'rxjs';
import { environment } from 'src/environments/environment';
import { EntityType } from '../models/entity-type';
import { JsonSchemaNormalizer } from '../models/json-schema-normalizer';
import { SchemaLoaderService } from './schema-loader.service';
import { MergedEntityType } from '../models/merged-entity-type';

interface OpenApiResponse {
  components: { schemas: Record<string, JSONSchema7> };
}

@Injectable({
  providedIn: 'root',
})
export class ApiSchemaLoaderService implements SchemaLoaderService {
  private readonly _openApiResponse$ = this._http
    .get<OpenApiResponse>(`${environment.apiBaseUrl}/openapi.json`)
    .pipe(shareReplay(1));

  private readonly _parser = new JsonSchemaNormalizer();

  constructor(private _http: HttpClient) {}

  private _schemaStreamCache = new Map<EntityType | MergedEntityType, Observable<JSONSchema7>>();
  loadSchema(type: EntityType | MergedEntityType): Observable<JSONSchema7> {
    if (!this._schemaStreamCache.has(type)) {
      const parsedSchema$ = this._getNormalizedSchema(type);
      this._schemaStreamCache.set(type, parsedSchema$.pipe(shareReplay(1)));
      console.log('SCHEMA CACHED', type);
    }
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    return this._schemaStreamCache.get(type)!;
  }

  private _getNormalizedSchema(type: EntityType | MergedEntityType) {
    return this._openApiResponse$.pipe(
      map((response) => {
        if (!(type in response.components.schemas)) {
          throw new Error(`Give type '${type}' doesn't exist in components/schema.`);
        }
        const schema = response.components.schemas[type];
        const parsedSchema = this._parser.normalize(schema, response);
        console.log('PARSED', parsedSchema);
        return parsedSchema;
      })
    );
  }
}
