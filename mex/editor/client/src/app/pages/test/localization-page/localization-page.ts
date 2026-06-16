import { Component } from "@angular/core";
import { TranslocoDirective } from "@jsverse/transloco";
import { TranslocoDatePipe, TranslocoCurrencyPipe, TranslocoDecimalPipe } from "@jsverse/transloco-locale";

@Component({
  selector: "app-localization-page",
  imports: [TranslocoDirective, TranslocoDatePipe, TranslocoCurrencyPipe, TranslocoDecimalPipe],
  templateUrl: "./localization-page.html",
  styleUrl: "./localization-page.scss",
})
export class LocalizationPage {
  date = new Date(2000, 0, 1); // 01.01.2000
  datetime = new Date(2000, 0, 1, 12, 30); // 01.01.2000 12:30
  decimal = 213.12345;
  money = 100000.12345;
}
