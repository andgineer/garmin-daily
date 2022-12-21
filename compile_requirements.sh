#!/usr/bin/env bash
#
# Pin current dependencies versions.
# If requirements* files already exists do nothing.
#

pip-compile requirements.dev.in
pip-compile requirements.in
