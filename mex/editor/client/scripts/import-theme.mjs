
// write script so it transforms the variable names to match actual usage? currently missmatched
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { dirname } from 'node:path';

const INPUT = process.argv[2] ?? 'theme-export/light.css';
const OUTPUT = process.argv[3] ?? 'src/theme-tokens.css';

if (!existsSync(INPUT)) {
  console.error(`Input file not found: ${INPUT}`);
  console.error(`Usage: node scripts/import-theme.mjs <input.css> <output.css>`);
  process.exit(1);
}

const input = readFileSync(INPUT, 'utf8');

const output = input
  .replace(/--md-sys-color-([a-z0-9-]+):/g, '--mat-sys-$1:')
  .replace(/^[^{]+\{/, ':root {'); // replace whatever the top selector is, not just ".light"

// script won't fail if src/styles/ doesn't exist yet
mkdirSync(dirname(OUTPUT), { recursive: true });
writeFileSync(OUTPUT, output);

console.log(`Wrote ${OUTPUT} from ${INPUT}`);
