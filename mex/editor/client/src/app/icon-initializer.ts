import { inject, provideAppInitializer } from "@angular/core";
import { MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";

// Gemeinsamer Kalenderrahmen (Ringe oben, Kopfleiste, Körper als Aussparung)
const FRAME =
  "M19 4h-1V2h-2v2H8V2H6v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 16H5V9h14v11z";

const svg = (...paths: string[]): string =>
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">${paths
    .map((d) => `<path d="${d}"/>`)
    .join("")}</svg>`;

/**
 * Icons for datepicker precisions.
 */
export const PRECISION_ICONS = {
  year: svg(
    FRAME,
    "M6.5 10.5h2v2h-2zM9.5 10.5h2v2h-2zM12.5 10.5h2v2h-2zM15.5 10.5h2v2h-2z" +
      "M6.5 13.5h2v2h-2zM9.5 13.5h2v2h-2zM12.5 13.5h2v2h-2zM15.5 13.5h2v2h-2z" +
      "M6.5 16.5h2v2h-2zM9.5 16.5h2v2h-2zM12.5 16.5h2v2h-2zM15.5 16.5h2v2h-2z",
  ),
  month: svg(
    FRAME,
    "M7 11h2v2H7zM11 11h2v2h-2zM15 11h2v2h-2zM7 15h2v2H7zM11 15h2v2h-2zM15 15h2v2h-2z",
  ),
  day: svg(FRAME, "M7 12h5v5H7z"),
  datetime: svg(
    "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16z",
    "M11 7h1.5v5.2l3.6 2.1-.75 1.25L11 13z",
  ),
} as const;

/**
 * AppInitializer that registers the precision icons as `precision-<name>` svg icons.
 */
export const iconAppInitializer = provideAppInitializer(() => {
  const iconRegistry = inject(MatIconRegistry);
  const sanitizer = inject(DomSanitizer);

  for (const [name, svgCode] of Object.entries(PRECISION_ICONS)) {
    iconRegistry.addSvgIconLiteral(`precision-${name}`, sanitizer.bypassSecurityTrustHtml(svgCode));
  }
});
