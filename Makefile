.PHONY: all test install karma linter prod stage dev
all: install test
test: linter karma

ifeq (, $(shell which npm))
$(error "npm not installed, follow https://github.com/nvm-sh/nvm")
endif

install:
	# install packages from lock file
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

prod:
	# build the prod angular package
	@ echo building prod package; \
	npm run ng build -- --configuration prod; \

stage:
	# build the stage angular package
	@ echo building stage package; \
	npm run ng build -- --configuration stage; \

dev:
	# build the dev angular package
	@ echo building dev package; \
	npm run ng build -- --configuration dev; \
