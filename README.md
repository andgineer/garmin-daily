[![Build Status](https://github.com/andgineer/garmin-daily/workflows/ci/badge.svg)](https://github.com/andgineer/garmin-daily/actions)
# Fill Google Sheets with data from Garmin Connect

# Documentation

[garmin-daily](https://andgineer.github.io/garmin-daily/)

# Developers

#### Min Python version

We use `Annotated` so at least Python 3.9

#### Create / activate environment
    . ./activate.sh

Delete `venv/` if you want to reinstall everything from requirements*.txt

    deactivate
    rm -f venv
    make reqs  # if you want to refresh versions
    pip install --upgrade pip-tools
    . ./activate.sh

#### Compile pinned to versions requirements*.txt from requirements*.in files
Using pip-tools

    make reqs

#### Release version
    make ver-bug/feature/release

Github actin will automatically update the pip package on pypi.org
