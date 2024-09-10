# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changes

- set fastapi, starlette and pydantic versions explicitly and update mex-common

### Deprecated

### Removed

### Fixed

### Security

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
