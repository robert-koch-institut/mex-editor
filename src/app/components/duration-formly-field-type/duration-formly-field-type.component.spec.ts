import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DurationFormlyFieldTypeComponent } from './duration-formly-field-type.component';

describe('DurationFormlyFieldTypeComponent', () => {
  let component: DurationFormlyFieldTypeComponent;
  let fixture: ComponentFixture<DurationFormlyFieldTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DurationFormlyFieldTypeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DurationFormlyFieldTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
