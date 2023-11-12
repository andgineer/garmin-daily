#!/usr/bin/env bash
#
# Extract docstrings to docs/
# make a copy for all languages
#

lazydocs \
    --output-path="./docs/api-reference" \
    --overview-file="index.md" \
    --src-base-url="https://github.com/andgineer/garmin-daily/blob/master/" \
    src/garmin_daily

mkdocs build --config-file docs/mkdocs-api-reference.yml
