# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- add color mode toggle to login screen
- added new/remove buttons for additive rules for string fields
- add event handlers for adding/removing additive value input cards
- added text input field for email, string and temporal fields
- add event handler for setting string input values

### Changes

- combine EditState.editor_fields and EditState.fields
- update transformation logic to handle strings from additive rules

### Deprecated

### Removed

### Fixed

### Security

## [0.10.0] - 2025-02-18

### Changes

- update mex-common to version 0.51.1
- pin mex-backend container version to 0.30.1
- update url parameters when search options change
- load url parameters on page load (i.e. when a link/bookmark is clicked)
- search parameters as state vars when switching editor components

## [0.9.0] - 2025-02-13

### Added

- aux extractor search for wikidata

### Changes

- update mex-common to version 0.49.3
- BREAKING: you must start the local dev mode simply with `pdm run editor` (no 2nd run)
- BREAKING: rename postfix_badge to render_badge (for consistency)
- simplify some styles and update look and feel to be more inline with mex-drop
- use more idiomatic variables for styling elements with colors or spacing

### Removed

- remove BackendIdentityProvider in favor of mex-common version
- remove identity_provider from EditorSettings in favor of mex-common setting
- remove EditorIdentityProvider enum in favor of mex-common enum
- remove dependency to reflex-chakra, use default checkboxes instead

### Fixed

- decorate state handlers with `@rx.event` to satisfy new reflex versions
- explicitly define cache strategies for vars with `@rx.var(cache=False)`

## [0.8.0] - 2025-01-22

### Added

- add toggles for preventive and subtractive rules
- add functionality to edit component for submitting rules
- add utility function to escalate errors to all consoles
- temporarily add BackendIdentityProvider (stop-gap MX-1763)

### Changes

- bump cookiecutter template to 57e9b7
- rename FixedX and EditableX classes to EditorX for consistency

### Removed

- drop dev-dependency to mex-backend, use the flush endpoint instead
- temporarily removed localization of temporals entity output

## [0.7.1] - 2025-01-15

- update mex-backend docker tag

## [0.7.0] - 2025-01-15

### Added

- redirect to original URL after login
- add icon identifiers to models.yaml and ModelConfig

## [0.6.0] - 2024-11-19

### Changes

- upgrade mex-common and model dependencies to v3
- overhaul and simplify margins and spaces
- move transform_models_to_fields from State to transform module
- use dedicated backend connector methods for edit and search
- use same rendering components for edit and search pages
- pop toasts when backend connector encounters errors
- scroll to top when pagination is triggered
- update dependency versions

### Fixed

- fix routing issues by moving the refresh handlers section from `on_mount` to `page.on_load`

## [0.5.0] - 2024-09-19

### Added

- implement simple search with pagination and entity type filtration

### Changes

- set fastapi, starlette and pydantic versions explicitly and update mex-common

## [0.4.0] - 2024-08-07

### Added

- implement a basic item view which will be expanded into the editing mode
- add model config YAML to store which fields to use for titles and previews
- add basic rendering functions for arbitrary models and types
- configure CI integration tests running against real backend and database
- implement integration tests for all four major pages in the editor

### Changes

- rework navigation bar to work with states instead of passing through literals
- update layout and styling on login form, merge page stub and search view

## [0.3.0] - 2024-07-29

### Added

- add login component and form
- add user menu in navbar with logout button
- setup authentication against locally configured users

### Changes

- re-organize state classes into individual modules

### Removed

- remove unused `mex.editor.transform.to_primitive`

## [0.2.1] - 2024-07-12

### Changes

- update dependency versions

## [0.2.0] - 2024-07-12

### Added

- add health check route to api

### Changes

- use production mode in dockerfile
- change default ports to 8030/8040

## [0.1.0] - 2024-06-14

### Changes

- switch tech stack to python, pydantic, fastapi and reflex
