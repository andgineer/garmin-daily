#!make
.HELP: docs

VERSION := $(shell cat src/garmin_daily/version.py | cut -d= -f2 | sed 's/\"//g; s/ //')
export VERSION

.HELP: version ## Show the current version
version:
	echo ${VERSION}

.HELP: ver-bug ## Bump the version for a bug
ver-bug:
	bash ./scripts/verup.sh bug

.HELP: ver-feature ## Bump the version for a feature
ver-feature:
	bash ./scripts/verup.sh feature

.HELP: ver-release ## Bump the version for a release
ver-release:
	bash ./scripts/verup.sh release

.HELP: reqs  ## Upgrade requirements including pre-commit
reqs:
	pre-commit autoupdate
	bash ./scripts/compile_requirements.sh
	pip install -r requirements.dev.txt
	pip install -r requirements.txt

.PHONY: docs # mark as phony so it always runs even we have a docs folder
.HELP: docs  ## Build the documentation
docs:
	bash ./scripts/build-docs.sh
	open -a "Google Chrome" http://127.0.0.1:8000/garmin-daily/
	mkdocs serve -f docs/mkdocs-en.yml

.HELP: docs-src  ## Build the API documentation from docstrings
docs-src:
	bash ./scripts/build-docs.sh
	open -a "Google Chrome" http://127.0.0.1:8000/garmin-daily/
	mkdocs serve -f docs/mkdocs-docstrings.yml

.HELP: help  ## Display this message
help:
	@grep -E \
		'^.HELP: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".HELP: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
