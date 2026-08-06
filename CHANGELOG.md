# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial Layout with header (including theme switcher and language switcher with noop) and footer
- Localization with Transloco and script to create model .po to .json files
- vitest/ui for better dev experience
- typedoc to generate typescript documentation
- docs to typescript components
- renovate rule for angular
- fasttrack create resource page
  - including basic fields only
- mex-fieldset component to mimic look of kernUx fieldset
- more linting rules
  - no commented out code
  - no unused imports in component (checked against template)
  - exported members must be documented
- pipes for typeToIconName, toLabel and toLookup
- new control fasttrack reference-select that allows to search for existing entites or create them.

### Changes

- ConceptOptions now use the new ToLookupPipe (which uses the LabelPipe, moved all lookup and label creation to spefic pipes).
- Grouped everything into fasttrack folder to meat the feature approach. Some components might be moved to shared
- new template https://github.com/robert-koch-institut/mex-template/releases/tag/1.3.0
- updated angular to 22.0.4
- updated template to https://github.com/robert-koch-institut/mex-template/commit/0d8c47
- alot of manual package updates to help renovatebot
- updated node to 24.15.0
- updated angular to 21.2.17
- renovate: group non-major npm updates into a single PR

### Deprecated

### Removed

### Fixed

- Tests fail if python tests dont complete successful
- TsDoc generation were not working due to merge failures

### Security

## [0.0.4] - 2026-04-28

### Changes

- update button text to test deployment

## [0.0.3] - 2026-04-28

### Fixed

- hardcode base hrefs again but include temporary `editor-ng` path

## [0.0.2] - 2026-04-27

### Fixed

- allow more base hrefs

## [0.0.1] - 2026-04-27

### Added

- setup docker compose and release pipeline
- configure easy debugging with vscode
- integrate backend proxy endpoint and show items in app

### Changes

- pin mex-common >= 1.19
- updated template to https://github.com/robert-koch-institut/mex-template/commit/af9ddc
- updated template to https://github.com/robert-koch-institut/mex-template/commit/172aac
- updated template to https://github.com/robert-koch-institut/mex-template/commit/43f715

### Security
