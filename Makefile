.PHONY: all test setup hooks install linter pytest wheel image run start docs
all: install test
test: linter pytest

LATEST = $(shell git describe --tags $(shell git rev-list --tags --max-count=1))
PWD = $(shell pwd)

setup:
	# install meta requirements system-wide
	@ echo installing requirements; \
	pip --disable-pip-version-check install --force-reinstall -r requirements.txt; \

hooks:
	# install pre-commit hooks when not in CI
	@ if [ -z "$$CI" ]; then \
		pre-commit install; \
	fi; \

install: setup hooks
	# install packages from lock file in local virtual environment
	@ echo installing package; \
	pdm install-all; \

linter:
	# run the linter hooks from pre-commit on all files
	@ echo linting all files; \
	pdm lint; \

pytest:
	# run the pytest test suite with unit and integration tests
	@ echo running all tests; \
	pdm test; \

wheel:
	# build the python package
	@ echo building wheel; \
	pdm wheel; \

image:
	# build the docker image
	@ echo building docker image mex-editor:${LATEST}; \
	export DOCKER_BUILDKIT=1; \
	pdm export --self --output locked-requirements.txt --no-hashes --without dev; \
	docker build \
		--tag rki/mex-editor:${LATEST} \
		--tag rki/mex-editor:latest .; \

run: image
	# run the service as a docker container
	@ echo running docker container mex-editor:${LATEST}; \
	docker run \
		--env MEX_EDITOR_API_HOST=0.0.0.0 \
		--publish 8030:8030 \
		--publish 8031:8031 \
		rki/mex-editor:${LATEST}; \

start: image
	# start the service using docker compose
	@ echo start mex-editor:${LATEST} with compose; \
	export DOCKER_BUILDKIT=1; \
	export COMPOSE_DOCKER_CLI_BUILD=1; \
	docker compose up mex-editor-frontend mex-editor-api mex-backend --remove-orphans; \

docs:
	# use sphinx to auto-generate html docs from code
	@ echo generating docs; \
	pdm doc; \
