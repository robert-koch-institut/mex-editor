# MEx editor

The editor enables anyone to create and edit entities in a simple and fast way.

[![cookiecutter](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/cookiecutter.yml/badge.svg)](https://github.com/robert-koch-institut/mex-template)
[![cve-scan](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/cve-scan.yml)
[![documentation](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/documentation.yml/badge.svg)](https://robert-koch-institut.github.io/mex-editor-ng)
[![linting](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/linting.yml)
[![testing](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/testing.yml/badge.svg)](https://github.com/robert-koch-institut/mex-editor-ng/actions/workflows/testing.yml)

## Project

The Metadata Exchange (MEx) project is committed to improve the retrieval of RKI
research data and projects. How? By focusing on metadata: instead of providing the
actual research data directly, the MEx metadata catalog captures descriptive information
about research data and activities. On this basis, we want to make the data FAIR[^1] so
that it can be shared with others.

Via MEx, metadata will be made findable, accessible and shareable, as well as available
for further research. The goal is to get an overview of what research data is available,
understand its context, and know what needs to be considered for subsequent use.

RKI cooperated with D4L data4life gGmbH for a pilot phase where the vision of a
FAIR metadata catalog was explored and concepts and prototypes were developed.
The partnership has ended with the successful conclusion of the pilot phase.

After an internal launch, the metadata will also be made publicly available and thus be
available to external researchers as well as the interested (professional) public to
find research data from the RKI.

For further details, please consult our
[project page](https://www.rki.de/DE/Aktuelles/Publikationen/Forschungsdaten/MEx/metadata-exchange-plattform-mex-node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

**Contact** \
For more information, please feel free to email us at [mex@rki.de](mailto:mex@rki.de).

### Publisher

**Robert Koch-Institut** \
Nordufer 20 \
13353 Berlin \
Germany

## Package

The editor is a web application for the MEx metadata catalog built with a FastAPI
backend and an Angular frontend. It provides a user-friendly interface for creating,
editing and managing metadata entities, making research data at RKI findable, accessible
and reusable.

### Client

The client is build with angular and lifes in `/mex/editor/client`. The directory is an isolated Node environment managed by `nodeenv`. To install node packages u can use `uv run exec-npm install <packagename>`. To exec angular specfic commands u can use `uv run exec-ng add <schematic>`.

Images have two locations depending on the usage:
- css: store images in `client/src/assets` and use relative code path to images `url("../assets/image.png")` to ensure basehref sass compiling is working correctly
- html: store images in `client/public` and use like `<img src="/image.png" />` where public dir acts as relative root.

### API

API is build with Fastapi and lifes in `mex/editor/api`and serves data specific for the editor under `/api/v0`. It includes a proxy for the `mex.backend` availabe under `/api/v0/backend`. The build angular client will be served under `/`.

## License

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## Development

### Installation

- install python on your system
- on unix, run `make install`
- on windows, run `.\mex.bat install`

### Running

- `uv run editor` to start the editor on configured port (default: 8000)
- `uv run editor --dev` to start the editor in watch mode (auto rebuild app) on configured port (default: 8000)

If u're using VSCode u can use the predefined launch configuration.

- `Run Editor (debug)` starts `editor-api-debug` and `angular-dev[edge]`
  - `editor-api-debugg` starts the API with debugpy and attach vscode debugger
  - `angular-dev[edge]` builds angular in dev mode using angular dev server and connect with edge

### Linting and testing

- run all linters with `make lint` or `.\mex.bat lint`
- run unit and integration tests with `make test` or `.\mex.bat test`
- run just the unit tests with `make unit` or `.\mex.bat unit`

### Updating dependencies

- update boilerplate files with `cruft update`
- update global requirements in `requirements.txt` manually
- update git hooks with `pre-commit autoupdate`
- update package dependencies using `uv sync --upgrade`
- update github actions in `.github/workflows/*.yml` manually
- update node modules/packages using `uv run exec-npm install`

### Creating release

- run `mex release RULE` to release a new version where RULE determines which part of
  the version to update and is one of `major`, `minor`, `patch`.

### Container workflow

- build image with `make image`
- run directly using docker `make run`
- start with docker compose `make start`

## Commands

- run `uv run {command} --help` to print instructions
- run `uv run {command} --debug` for interactive debugging

### Editor

- `uv run install-frontend` install Node.js dependencies
- `uv run build-frontend` build the Angular frontend for production
- `uv run install-and-build-frontend` install dependencies and build
- `uv run editor` start the editor api and frontend simultaneously
- `uv run editor --dev` starts the editor api and frontend with hot reload
- `uv run editor --startup frontend` start only the frontend
- `uv run editor --startup api` start only the backend
- `uv run test-frontend` run frontend tests and start api automatically
- `uv run pytest` run python backend api tests with pytest

### Node

- `uv run exec-npm audit fix` audit node dependencies
- `uv run exec-npm run ng lint` run ESLint on the Angular frontend
- `uv run exec-npm run ng lint -- --fix` run ESLint with auto-fix
- `uv run exec-npx prettier --check src` check formatting
- `uv run exec-npx prettier --write src` auto-format frontend code
- `uv run exec-npm run test` run frontend unit tests
- `uv run exec-npm run start` start Angular dev server with live reload
- `uv run exec-npm run watch` build frontend in watch mode
- `uv run exec-npm install --package-lock-only` to update the lock file
