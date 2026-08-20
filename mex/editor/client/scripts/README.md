# Updating the app theme from Figma

Our color theming is generated in Figma using the **Material Theme Builder**
plugin, and imported into this Angular app as Material 3 design tokens. This
document explains how to pull in a new export whenever the design changes.

## How it works

1. A designer adjusts colors in Figma using the Material Theme Builder plugin.
2. They export the theme as CSS (`light.css`, `dark.css`, etc.).
3. We run a conversion script that renames the plugin's token names
   (`--md-sys-color-*`) to the names Angular Material expects
   (`--mat-sys-*`), and rewrites the file to apply globally (`:root`).
4. The converted file (`src/theme-tokens.css`) is committed to the repo and
   loaded after our base theme, so it overrides Angular Material's default
   colors everywhere `mat-*` components are used.

## Getting a new export

1. Open the Figma file and the Material Theme Builder plugin.
2. Export the theme as CSS.
3. Unzip the export and locate `light.css`. (we currently don't use dark themes)
4. Copy `light.css` into `theme-export/` in this repo.

## Running the import

```powershell
uv run python mex/editor/client/scripts/import_theme.py <path to input file> <path to output file>
```

## Where things live

```
mex/editor/client/
├── scripts/
│   └── import_theme.py      # conversion script
├── src/
│   ├── styles.scss           # base Angular Material theme
│   └── theme-tokens.css      # generated — committed to git
├── theme-export/             # raw Figma export lands here — gitignored
└── package.json              # "theme:import" script entry
```
