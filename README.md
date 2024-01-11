# MEx editor

Metadata editor web application.

[![linting](https://github.com/robert-koch-institut/mex-editor/actions/workflows/linting.yml/badge.svg)](https://github.com/robert-koch-institut/mex-editor/actions/workflows/linting.yml)
[![cve-scan](https://github.com/robert-koch-institut/mex-editor/actions/workflows/cve-scan.yml/badge.svg)](https://github.com/robert-koch-institut/mex-editor/actions/workflows/cve-scan.yml)

## project

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
[project page](https://www.rki.de/DE/Content/Forsch/MEx/MEx_node.html).

[^1]: FAIR is referencing the so-called
[FAIR data principles](https://www.go-fair.org/fair-principles/) – guidelines to make
data Findable, Accessible, Interoperable and Reusable.

## package

The `mex-editor` is an angular application that allows creating and editing rules to
non-destructivley manipulate metadata. This can be used to enrich data with manual input
or insert new data from scratch.

## license

This package is licensed under the [MIT license](/LICENSE). All other software
components of the MEx project are open-sourced under the same license as well.

## development

### installation

#### unix

- get https://github.com/nvm-sh/nvm
- run `nvm install --lts`
- run `npm install`
- run `npm run prepare`

#### windows

- get https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-windows
- run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`
- run `nvm install --lts`
- run `npm install`
- run `npm run prepare`

### start

- run `npm start`

### lint

- run `npm run lint`

### test

- run `npm test`

### build

- run `npm run build`
