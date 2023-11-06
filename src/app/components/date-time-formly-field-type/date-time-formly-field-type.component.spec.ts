import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DateTimeFormlyFieldTypeComponent } from './date-time-formly-field-type.component';

describe('DateTimeFormlyFieldTypeComponent', () => {
  let component: DateTimeFormlyFieldTypeComponent;
  let fixture: ComponentFixture<DateTimeFormlyFieldTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [DateTimeFormlyFieldTypeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(DateTimeFormlyFieldTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
