// @ts-check
const eslint = require("@eslint/js");
const { defineConfig } = require("eslint/config");
const tseslint = require("typescript-eslint");
const angular = require("angular-eslint");
const security = require("eslint-plugin-security");

module.exports = defineConfig([
  {
    files: ["**/*.ts"],
    extends: [
      eslint.configs.recommended,
      tseslint.configs.recommended,
      tseslint.configs.stylistic,
      angular.configs.tsRecommended,
    ],
    plugins: {
      security
    },
    languageOptions: {
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    processor: angular.processInlineTemplates,
    rules: {
      // TODO(FE): remove/change when eslit-angular got an update @see {@link https://github.com/angular-eslint/angular-eslint/blob/main/packages/eslint-plugin/docs/rules/prefer-on-push-component-change-detection.md#rationale}
      "@angular-eslint/prefer-on-push-component-change-detection": ["warn"],
      "@angular-eslint/directive-selector": [
        "error",
        {
          type: "attribute",
          prefix: "app",
          style: "camelCase",
        },
      ],
      "@angular-eslint/component-selector": [
        "error",
        {
          type: "element",
          prefix: "app",
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
      "max-lines-per-function": ["error", 100],
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
    extends: [angular.configs.templateRecommended, angular.configs.templateAccessibility],
    rules: {},
  },
]);
