.PHONY: help
help:
	@echo analyze    - run the type checker
	@echo check      - run tests
	@echo check-fast - run non-network, non-subprocess tests
	@echo clean      - delete build artifacts
	@echo format     - format the code

.PHONY: analyze
analyze:
	poetry run mypy . tests/

.PHONY: build
build:
	poetry build

.PHONY: check
check: analyze
	poetry run pytest

.PHONY: check-fast
check-fast: analyze
	poetry run pytest -m "not network and not subprocess"

.PHONY: clean
clean:
	rm -rf dist/
	rm -rf pyrs990.egg-info/

ORG_NAME := codeformontana
IMAGE_NAME := pyrs990
FULL_VERSION := $(shell poetry version | cut -d ' ' -f 2)
MINOR_VERSION := $(shell poetry version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
MAJOR_VERSION := $(shell poetry version | cut -d ' ' -f 2 | cut -d '.' -f 1)

.PHONY: docker-build
docker-build:
	docker build -t $(ORG_NAME)/$(IMAGE_NAME):$(FULL_VERSION) \
				 -t $(ORG_NAME)/$(IMAGE_NAME):$(MINOR_VERSION) \
				 -t $(ORG_NAME)/$(IMAGE_NAME):$(MAJOR_VERSION) \
				 -t $(ORG_NAME)/$(IMAGE_NAME):latest \
				 .
	docker run --mount src="${PWD}/data",target=/data,type=bind pyrs990:latest --version

.PHONY: docker-push
docker-push:
	docker push $(ORG_NAME)/$(IMAGE_NAME):$(FULL_VERSION) \
				$(ORG_NAME)/$(IMAGE_NAME):$(MINOR_VERSION) \
				$(ORG_NAME)/$(IMAGE_NAME):$(MAJOR_VERSION) \
				$(ORG_NAME)/$(IMAGE_NAME):latest

.PHONY: format
format:
	poetry run isort --recursive --use-parentheses --trailing-comma -y -w 80
	poetry run autoflake -r --in-place --remove-unused-variables .
	poetry run black -t py38 -l 80 .

.PHONY: format-check
format-check:
	poetry run black -t py38 -l 80 --check .

.PHONY: publish
publish:
	poetry publish

.PHONY: store-version
store-version:
	$(echo $(FULL_VERSION) > pyrs990/version.txt)

.PHONY: version-major
version-major:
	poetry version major
	$(MAKE) store-version

.PHONY: version-minor
version-minor:
	poetry version minor
	$(MAKE) store-version

.PHONY: version-patch
version-patch:
	poetry version patch
	$(MAKE) store-version
