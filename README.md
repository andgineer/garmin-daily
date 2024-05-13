# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/andgineer/garmin-daily/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                      |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------ | -------: | -------: | ------: | --------: |
| src/garmin\_daily/columns\_mapper.py      |       25 |        1 |     96% |        75 |
| src/garmin\_daily/garmin\_aggregations.py |      187 |        2 |     99% |   171-172 |
| src/garmin\_daily/google\_sheet.py        |      128 |       11 |     91% |150, 189, 201-202, 248, 295-297, 301-302, 373 |
| src/garmin\_daily/snake\_to\_camel.py     |        7 |        0 |    100% |           |
| src/garmin\_daily/version.py              |        1 |        0 |    100% |           |
|                                 **TOTAL** |  **348** |   **14** | **96%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/andgineer/garmin-daily/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/garmin-daily/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/andgineer/garmin-daily/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/garmin-daily/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fandgineer%2Fgarmin-daily%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/andgineer/garmin-daily/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.