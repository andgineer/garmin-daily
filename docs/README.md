# garmin-dayly

Fill Google Sheets with fitness data from Garmin Connect.

## Installation

    pip install garmin-daily

## Credentials

### Garmin Connect
Place into env var `GARMIN_EMAIL` and `GARMIN_PASSWORD` respectfully.

### Google Sheets
Get Google credentials for Google Sheet as explained in [gspread:Using Service Account](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)
Place it to `~/.config/gspread/service_account.json`.

Do not forget to grant access to you sheets for this service emails.

## Google Sheet structure

Expected columns:

- Location
- Sport
- Duration
- Date
- Distance
- Steps
- Comment
- Week
- Hours
- Week Day
- HR rest
- Sleep time
- VO2 max

First row should be with the columns' titles.

Application look for column with date using the title "Date".
But for the moment application ignores title row when creates fitnes data rows
https://github.com/andgineer/garmin-daily/issues/2.

## garmin-daily command line interface

To add rows to Google Sheet from Garmin Connect, use

    garmin-daily --help

At minimum you specify Google Sheet name and that's all

    garmin-daily --sheet "My Fitness"

It also can automatically create you gym trainings if you have them
on specific days.
It's easier to correct already created rows then to create them
manually from scratch.

List the week days with gym trainings in the parameters
and specify your gym location and usual training duration:

    garmin-daily --sheet "My Fitness" \
        -g mon -g tue -g fri \
        --gym-duration 30 \
        --gym-location "Cool place"

If for some reason you use in the Google Sheet locale different from
the one on your PC.
For example on your PC it is `USA` locale with digital point separator "."
but in the Google Sheet it's `Russia` with separator ",".

In such case you can specify Google Sheet locale in the CLI -
sorry no automation here for the moment
https://github.com/andgineer/garmin-daily/issues/1.

    garmin-daily --sheet "My Fitness" \
        --sheet-locale "ru_RU"

# Docstrings documentation

Documentation generated from source code.

[reference](docstrings/)

# source code

[sorokin.engineer/aios3](https://github.com/andgineer/garmin-daily)
