.PHONY: all test install karma linter build
all: install test
test: linter karma

ifeq (, $(shell which npm))
$(error "npm not installed, follow https://github.com/nvm-sh/nvm")
endif

install:
	# run the npm installation
	@ echo installing package; \
	npm install; \

linter:
	# run the linter hooks configured in package.json
	@ echo linting all files; \
	npm run lint; \

karma:
	# run the karma test suite with all tests
	@ echo running all tests; \
	npm run test; \

build:
	# build the angular package
	@ echo building package; \
	npm run build --prod; \
