import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { JSONSchema7 } from 'json-schema';
import * as _ from 'lodash-es';
import { map, Observable, of, switchMap } from 'rxjs';
import { metadataEditorPrimarySourceId, uneditableEntityFields } from 'src/app/models/constants';
import { Entity } from 'src/app/models/entity';
import { NewEntityRuleSet } from 'src/app/models/entity-rule-set';
import { isEntityType } from 'src/app/models/entity-type';
import { AssetsEntityRuleSetSaverService } from 'src/app/services/assets-entity-rule-set-saver.service';
import { SchemaLoaderService } from 'src/app/services/schema-loader.service';

@Component({
  selector: 'app-entity-new-page',
  templateUrl: './entity-new-page.component.html',
  styleUrls: ['./entity-new-page.component.scss'],
})
export class EntityNewPageComponent implements OnInit {
  entityCreation$?: Observable<{ entity: Entity; schema: JSONSchema7 } | undefined>;
  isSaving = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private schemaLoader: SchemaLoaderService,
    private ruleSetSaver: AssetsEntityRuleSetSaverService
  ) {}
  ngOnInit(): void {
    this.entityCreation$ = this.route.paramMap.pipe(
      switchMap((x) => {
        if (x.has('entitytype')) {
          const etParam = x.get('entitytype');
          if (isEntityType(etParam)) {
            return this.schemaLoader.loadSchema(etParam).pipe(
              map((x) => ({
                entity: {
                  $type: etParam,
                  identifier: '',
                  stableTargetId: '',
                  hadPrimarySource: '',
                },
                schema: x,
              }))
            );
          }
        }
        return of(undefined);
      })
    );
  }

  save(entity?: Entity) {
    if (entity) {
      this.isSaving = true;
      const ruleSet = this.entityToRuleSet(entity);
      this.ruleSetSaver.save(ruleSet).subscribe((x) => {
        this.isSaving = false;
        this.router.navigate(['/item', x.stableTargetId]);
      });
    }
  }

  private entityToRuleSet(entity: Entity): NewEntityRuleSet {
    const result: NewEntityRuleSet = {
      hadPrimarySource: metadataEditorPrimarySourceId,
    };

    _.forEach(entity, (x, key) => {
      if (!uneditableEntityFields.includes(key)) {
        result[key] = { addValue: x };
      }
    });

    return result;
  }
}
