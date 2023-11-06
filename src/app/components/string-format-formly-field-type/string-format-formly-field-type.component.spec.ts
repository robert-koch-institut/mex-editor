import { ComponentFixture, TestBed } from '@angular/core/testing';

import { StringFormatFormlyFieldTypeComponent } from './string-format-formly-field-type.component';

describe('StringFormatFormlyFieldTypeComponent', () => {
  let component: StringFormatFormlyFieldTypeComponent;
  let fixture: ComponentFixture<StringFormatFormlyFieldTypeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [StringFormatFormlyFieldTypeComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(StringFormatFormlyFieldTypeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
