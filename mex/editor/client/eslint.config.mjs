// @ts-check
import eslint from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";
import angular from "angular-eslint";
import security from "eslint-plugin-security";
import noCommentedOutCode from "./eslint-rules/no-commented-out-code.mjs";
import prettierRecommended from "eslint-plugin-prettier/recommended";
import typedocPlugin from "eslint-plugin-typedoc";
import importSortPlugin from "eslint-plugin-simple-import-sort";
import perfectionist from "eslint-plugin-perfectionist";

const config = defineConfig([
  {
    ...typedocPlugin.configs.recommended,
    settings: {
      typedoc: {
        // Weist den Linter an, Decorators als Teil des nachfolgenden Knotens zu betrachten
        ignoreDecorators: true,
      },
      // ignoreDecorators: true,
    },
  },
  {
    files: ["**/*.ts"],
    extends: [
      prettierRecommended,
      eslint.configs.recommended,
      tseslint.configs.recommended,
      tseslint.configs.stylistic,
      angular.configs.tsRecommended,
    ],
    plugins: {
      // @ts-ignore
      security,
      // @ts-ignore
      local: { rules: { "no-commented-out-code": noCommentedOutCode } },
      "simple-import-sort": importSortPlugin,
      perfectionist,
    },
    languageOptions: {
      parserOptions: {
        projectService: true,
      },
    },
    processor: angular.processInlineTemplates,
    rules: {
      "perfectionist/sort-arrays": [
        "error",
        {
          type: "alphabetical",
          order: "asc",
          useConfigurationIf: {
            matchesAstSelector:
              'Decorator[expression.callee.name="Component"] Property[key.name="imports"] ArrayExpression',
          },
        },
        {
          type: "unsorted", // fallback: don't touch other arrays
          useConfigurationIf: {},
        },
      ],
      "simple-import-sort/imports": "error",
      "simple-import-sort/exports": "error",
      "prettier/prettier": ["error", { endOfLine: "auto" }],
      "local/no-commented-out-code": "warn",
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "mex",
          style: "camelCase",
        },
      ],
      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "mex",
          style: "kebab-case",
        },
      ],
      // ruff TC001-010 typing-only imports
      "@typescript-eslint/consistent-type-imports": [
        "error",
        { prefer: "type-imports", fixStyle: "separate-type-imports" },
      ],
      // ruff PGH003 blanket-type-ignore
      "@typescript-eslint/ban-ts-comment": [
        "error",
        {
          "ts-ignore": "allow-with-description",
          "ts-expect-error": "allow-with-description",
          "ts-nocheck": "allow-with-description",
          "ts-check": false,
          minimumDescriptionLength: 10,
        },
      ],
      // ruff F401/F841/ARG001-005
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      // ruff T100/T201/T203
      "no-debugger": "error",
      "no-console": ["error", { allow: ["warn", "error"] }],
      // ruff RET505/RET501/SIM103
      "no-else-return": "error",
      "no-useless-return": "error",
      "no-lonely-if": "error",
      // ruff EM101/102/103
      "@typescript-eslint/only-throw-error": "error",
      // ruff A001-A006 builtin-shadowing
      "no-shadow": "off",
      "@typescript-eslint/no-shadow": "error",
      // ruff C901 / PLR0911-0915 complexity caps
      complexity: ["error", 12],
      "max-params": ["error", 5],
      "max-statements": ["error", 50],
      "max-lines-per-function": ["error", { max: 100, skipBlankLines: true, skipComments: true }],
      // ruff N801-N818 naming (JS-flavored)
      "@typescript-eslint/naming-convention": [
        "error",
        { selector: "default", format: ["camelCase"], leadingUnderscore: "allow" },
        { selector: "variable", format: ["camelCase", "UPPER_CASE"], leadingUnderscore: "allow" },
        { selector: "parameter", format: ["camelCase"], leadingUnderscore: "allow" },
        { selector: "typeLike", format: ["PascalCase"] },
        { selector: "enumMember", format: ["PascalCase", "UPPER_CASE"] },
        { selector: "import", format: ["camelCase", "PascalCase"] },
      ],
      // ruff S307 suspicious-eval-usage
      "security/detect-eval-with-expression": "error",
    },
  },
  {
    files: ["**/*.html"],
    extends: [
      prettierRecommended,
      angular.configs.templateRecommended,
      angular.configs.templateAccessibility,
    ],
    rules: {
      "prettier/prettier": ["error", { endOfLine: "auto" }],
    },
  },
]);

export default config;
