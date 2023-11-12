[![Build Status](https://github.com/andgineer/garmin-daily/workflows/Test/badge.svg)](https://github.com/andgineer/garmin-daily/actions)
[![Coverage](https://raw.githubusercontent.com/andgineer/garmin-daily/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/garmin-daily/blob/python-coverage-comment-action-data/htmlcov/index.html)
# Fill Google Sheets with data from Garmin Connect

![garmin-daily.png](https://andgineer.github.io/garmin-daily/en/garmin-daily.png)

## User manual

[garmin-daily](https://andgineer.github.io/garmin-daily/en/)

## Developers
### API
[Auto-generated reference](https://andgineer.github.io/garmin-daily/api-reference/).

```python
daily = GarminDaily()
daily.login()
day = daily[datetime.date(2023, 4, 15)]
print(day.total_steps)
```

### Create / activate environment
    . ./activate.sh

It will also install the package in [edit mode](https://realpython.com/what-is-pip/#installing-packages-in-editable-mode-to-ease-development).

### pre-commit
Do not forget to install, so static check github action won't fail on your commits

    pip install pre-commit
    pre-commit install  # in the project folder

### Scripts
    make help

### Garmin Connect credentials
[user manual](https://andgineer.github.io/garmin-daily/en/)

## Coverage report
* [Codecov](https://app.codecov.io/gh/andgineer/garmin-daily/tree/main/src%2Fgarmin_daily)
* [Coveralls](https://coveralls.io/github/andgineer/garmin-daily)
