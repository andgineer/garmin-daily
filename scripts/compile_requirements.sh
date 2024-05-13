#!/usr/bin/env bash
#
# Pin current dependencies versions.
#

rm -f requirements.txt
rm -f requirements.dev.txt

pip-compile requirements.dev.in --upgrade
pip-compile requirements.in --upgrade
