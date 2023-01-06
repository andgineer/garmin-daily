[![Build Status](https://github.com/andgineer/garmin-daily/workflows/ci/badge.svg)](https://github.com/andgineer/garmin-daily/actions)
# Fill Google Sheets with data from Garmin Connect

![garmin-daily.png](docs%2Fgarmin-daily.png)

# Documentation

Detailed user manual [garmin-daily](https://andgineer.github.io/garmin-daily/)

# Developers

#### Min Python version

We use `Annotated` so at least Python 3.9

#### pre-commit

Do not forget to install, so static check github action won't fail on your commits

    pip install pre-commit
    pre-commit install  # in the project folder

#### Create / activate environment
    . ./activate.sh

Delete `venv/` if you want to reinstall everything from requirements*.txt

    make reqs  # if you want to refresh dependencies
    deactivate
    rm -f venv
    pip install --upgrade pip-tools
    . ./activate.sh

#### Compile pinned to versions requirements*.txt from requirements*.in files
Using pip-tools

    make reqs

#### Release version
    make ver-bug/feature/release

Github actin will automatically update the pip package on pypi.org

#### Docs

Github pages https://andgineer.github.io/garmin-daily/ are auto created from markdown files
in `docs/`.

# Autodocs

Documentation generated from docstrings in sources:

[reference](docstrings/)
