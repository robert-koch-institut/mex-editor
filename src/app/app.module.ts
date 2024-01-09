import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HomePageComponent } from './pages/home-page/home-page.component';
import { MatAutocompleteModule } from '@angular/material/autocomplete';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule, MatIconRegistry } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTableModule } from '@angular/material/table';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatDialogModule, MAT_DIALOG_DEFAULT_OPTIONS } from '@angular/material/dialog';
import { NgModule } from '@angular/core';
import { FormlyModule } from '@ngx-formly/core';
import { FormlyMaterialModule } from '@ngx-formly/material';
import { HttpClientModule } from '@angular/common/http';
import { MatSelectModule } from '@angular/material/select';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { ObjectFormlyFieldTypeComponent } from './components/object-formly-field-type/object-formly-field-type.component';
import { ArrayFormlyFieldTypeComponent } from './components/array-formly-field-type/array-formly-field-type.component';
import { EntityTypeLabelPipe } from './pipes/entity-type-label.pipe';
import { EntityLookupFormlyFieldTypeComponent } from './components/entity-lookup-formly-field-type/entity-lookup-formly-field-type.component';
import { MergedEntitySearchDialogComponent } from './components/merged-entity-search-dialog/merged-entity-search-dialog.component';
import { MergedEntityListComponent } from './components/merged-entity-list/merged-entity-list.component';
import { MultiSchemaFormlyFieldTypeComponent } from './components/multi-schema-formly-field-type/multi-schema-formly-field-type.component';
import { FormlyMatDatepickerModule } from '@ngx-formly/material/datepicker';
import { de } from 'date-fns/locale';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';
import { DateFnsAdapter, MAT_DATE_FNS_FORMATS } from '@angular/material-date-fns-adapter';
import { DurationFormlyFieldTypeComponent } from './components/duration-formly-field-type/duration-formly-field-type.component';
import { DurationControlComponent } from './components/duration-control/duration-control.component';
import { StringFormatFormlyFieldTypeComponent } from './components/string-format-formly-field-type/string-format-formly-field-type.component';
import { DateTimeFormlyFieldTypeComponent } from './components/date-time-formly-field-type/date-time-formly-field-type.component';
import { MatRadioModule } from '@angular/material/radio';
import {
  NgxMatDatetimePickerModule,
  NgxMatNativeDateModule,
  NgxMatTimepickerModule,
  NGX_MAT_DATE_FORMATS,
  NGX_MAT_NATIVE_DATE_FORMATS,
} from '@angular-material-components/datetime-picker';
import { orderFieldGroupExtension } from './models/formly-order-extention';
import { EntityNewPageComponent } from './pages/entity-new-page/entity-new-page.component';
import { EntityEditPageComponent } from './pages/entity-edit-page/entity-edit-page.component';
import { EntitySearchPageComponent } from './pages/entity-search-page/entity-search-page.component';
import { EntityEditFormComponent } from './components/entity-edit-form/entity-edit-form.component';
import { PageNotFoundPageComponent } from './pages/page-not-found-page/page-not-found-page.component';
import { MergedEntitySearchComponent } from './components/merged-entity-search/merged-entity-search.component';
import { EntityTypeIconPipe } from './pipes/entity-type-icon.pipe';
import { RuleSetPreviewComponent } from './components/rule-set-preview/rule-set-preview.component';
import { RuleSetSaveDialogComponent } from './components/rule-set-save-dialog/rule-set-save-dialog.component';
import { BlockValueFormlyFieldWrapperComponent } from './components/block-value-formly-field-wrapper/block-value-formly-field-wrapper.component';
import { EntitiesRuleSetEditComponent } from './components/entities-rule-set-edit/entities-rule-set-edit.component';
import { EntityRuleSetFieldEditComponent } from './components/entity-rule-set-field-edit/entity-rule-set-field-edit.component';
import { AddValueRuleSetFieldEditComponent } from './components/add-value-rule-set-field-edit/add-value-rule-set-field-edit.component';
import { A11yModule } from '@angular/cdk/a11y';
import { createFormlyWrapperMap, FORMLY_WRAPPER_MAP } from './util/create-formly-wrapper-map';
import { MergedEntityDisplayComponent } from './components/merged-entity-display/merged-entity-display.component';
import { LoadEntityPipe } from './pipes/load-entity.pipe';
import { NgLetModule } from 'ng-let';
import { FirstPipe } from './pipes/first.pipe';
import { DebugSearchPageComponent } from './pages/debug-search-page/debug-search-page.component';
import { StringFormatPipe } from './pipes/string-format.pipe';
import { registerLocaleData } from '@angular/common';
import localeDe from '@angular/common/locales/de';
import localeDeExtra from '@angular/common/locales/extra/de';
import { HasKeyPipe } from './pipes/has-key.pipe';
import { SchemaLoaderService } from './services/schema-loader.service';
import { ApiSchemaLoaderService } from './services/api-schema-loader.service';
import { DebugEditPageComponent } from './pages/debug-edit-page/debug-edit-page.component';
import { MatTabsModule } from '@angular/material/tabs';
import { OkCancelDialogComponent } from './components/ok-cancel-dialog/ok-cancel-dialog.component';
import { EntityRuleSetLoaderService } from './services/entity-rule-set-loader.service';
import { ApiEntityRuleSetLoaderService } from './services/api-entity-rule-set-loader.service';
import { EntityLoaderService } from './services/entity-loader.service';
import { ApiEntityLoaderService } from './services/api-entity-loader.service';
import { EntitySearchService } from './services/entity-search.service';
import { ApiEntitySearchService } from './services/api-entity-search.service';
import { EntityRuleSetSaverService } from './services/entity-rule-set-saver.service';
import { ApiEntityRuleSetSaverService } from './services/api-entity-rule-set-saver.service';
import { EntityRuleSetPreviewService } from './services/entity-rule-set-preview.service';
import { ApiEntityRuleSetPreviewService } from './services/api-entity-rule-set-preview.service';
import { LoadingLabelFakeComponent } from './components/loading-label-fake/loading-label-fake.component';
import { LoadingMergedEntityComponent } from './components/loading-merged-entity/loading-merged-entity.component';
import { SatPopoverModule } from '@wjaspers/sat-popover';
import { EntityLinkDialogComponent } from './components/entity-link-dialog/entity-link-dialog.component';
import { EntityLoadByIdComponent } from './components/entity-load-by-id/entity-load-by-id.component';
import { LoadingComponent } from './components/loading/loading.component';

registerLocaleData(localeDe, 'de', localeDeExtra);

const dateTimeFormats = {
  ...NGX_MAT_NATIVE_DATE_FORMATS,
  display: {
    ...NGX_MAT_NATIVE_DATE_FORMATS.display,
    dateInput: {
      ...NGX_MAT_NATIVE_DATE_FORMATS.display.dateInput,
      month: '2-digit',
      day: '2-digit',
    },
  },
};

@NgModule({
  declarations: [
    AppComponent,
    HomePageComponent,
    ObjectFormlyFieldTypeComponent,
    ArrayFormlyFieldTypeComponent,
    EntityTypeLabelPipe,
    MultiSchemaFormlyFieldTypeComponent,
    EntityLookupFormlyFieldTypeComponent,
    MergedEntitySearchDialogComponent,
    MergedEntityListComponent,
    DurationFormlyFieldTypeComponent,
    DurationControlComponent,
    StringFormatFormlyFieldTypeComponent,
    DateTimeFormlyFieldTypeComponent,
    EntityNewPageComponent,
    EntityEditPageComponent,
    EntitySearchPageComponent,
    EntityEditFormComponent,
    PageNotFoundPageComponent,
    MergedEntitySearchComponent,
    EntityTypeIconPipe,
    RuleSetPreviewComponent,
    RuleSetSaveDialogComponent,
    BlockValueFormlyFieldWrapperComponent,
    EntitiesRuleSetEditComponent,
    EntityRuleSetFieldEditComponent,
    AddValueRuleSetFieldEditComponent,
    MergedEntityDisplayComponent,
    LoadEntityPipe,
    FirstPipe,
    DebugSearchPageComponent,
    StringFormatPipe,
    HasKeyPipe,
    DebugEditPageComponent,
    OkCancelDialogComponent,
    LoadingLabelFakeComponent,
    LoadingMergedEntityComponent,
    EntityLinkDialogComponent,
    EntityLoadByIdComponent,
    LoadingComponent,
  ],
  imports: [
    AppRoutingModule,
    BrowserAnimationsModule,
    BrowserModule,
    FormsModule,
    MatAutocompleteModule,
    MatButtonModule,
    NgLetModule,
    FormlyMatDatepickerModule,
    HttpClientModule,
    MatChipsModule,
    MatSlideToggleModule,
    MatFormFieldModule,
    A11yModule,
    MatIconModule,
    MatSelectModule,
    SatPopoverModule,
    MatDialogModule,
    MatMenuModule,
    MatInputModule,
    MatDatepickerModule,
    MatProgressSpinnerModule,
    MatListModule,
    MatPaginatorModule,
    MatTableModule,
    MatRadioModule,
    MatTabsModule,
    MatToolbarModule,
    MatSnackBarModule,
    NgxMatDatetimePickerModule,
    NgxMatNativeDateModule,
    NgxMatTimepickerModule,
    ReactiveFormsModule,
    ReactiveFormsModule,
    FormlyModule.forRoot({
      types: [
        { name: 'object', component: ObjectFormlyFieldTypeComponent },
        { name: 'array', component: ArrayFormlyFieldTypeComponent },
        {
          name: 'entity-lookup',
          component: EntityLookupFormlyFieldTypeComponent,
          wrappers: ['form-field'],
        },
        { name: 'multischema', component: MultiSchemaFormlyFieldTypeComponent },
        { name: 'duration', component: DurationFormlyFieldTypeComponent },
        {
          name: 'string-format',
          component: StringFormatFormlyFieldTypeComponent,
        },
        {
          name: 'datetime',
          component: DateTimeFormlyFieldTypeComponent,
          wrappers: ['form-field'],
        },
      ],
      validationMessages: [
        {
          name: 'required',
          message: 'Dieses Feld ist ein Pflichtfeld und muss ausgefüllt werden.',
        },
        {
          name: 'pattern',
          message: (...args) => {
            return `Der angegeben Wert entspricht nicht dem Pattern '${args[0].requiredPattern}'.`;
          },
        },
      ],
      extensions: [{ name: 'order-fieldgroup', extension: orderFieldGroupExtension }],
      wrappers: [
        {
          name: 'block-value-wrapper',
          component: BlockValueFormlyFieldWrapperComponent,
        },
      ],
    }),
    FormlyMaterialModule,
  ],
  providers: [
    { provide: MAT_DATE_LOCALE, useValue: de },
    { provide: DateAdapter, useClass: DateFnsAdapter },
    { provide: MAT_DATE_FORMATS, useValue: MAT_DATE_FNS_FORMATS },
    { provide: NGX_MAT_DATE_FORMATS, useValue: dateTimeFormats },
    { provide: FORMLY_WRAPPER_MAP, useFactory: () => createFormlyWrapperMap() },
    {
      provide: MAT_DIALOG_DEFAULT_OPTIONS,
      useValue: { width: '61.8vw', height: '61.8vh' },
    },
    { provide: SchemaLoaderService, useClass: ApiSchemaLoaderService },
    { provide: EntityRuleSetLoaderService, useClass: ApiEntityRuleSetLoaderService },
    { provide: EntityRuleSetSaverService, useClass: ApiEntityRuleSetSaverService },
    { provide: EntityLoaderService, useClass: ApiEntityLoaderService },
    { provide: EntitySearchService, useClass: ApiEntitySearchService },
    { provide: EntityRuleSetPreviewService, useClass: ApiEntityRuleSetPreviewService },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {
  constructor(private _iconRegistry: MatIconRegistry) {
    _iconRegistry.setDefaultFontSetClass('material-symbols-outlined');
  }
}
