# garmin-dayly

Fill Google Sheets with data from Garmin Connect.

## Goodreads export to markdown files

If you want to import your book reviews for example to Obsidian, all you need it to convert goodreads export CSV
to markdown files.

I included simple script for that to this package.

Just install the package

    pip install garmin-dayly

And it will also install script `goodreads_csv_to_markdown`.
Call it as `goodreads_csv_to_markdown --help` to get help.

## Get Google Sheets credentials
Get Google credentials for Google Sheet as explained in [gspread:Using Service Account](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)
Place it to `~/.config/gspread/service_account.json`.

Do not forget to grant access to you sheets for this service emails.


# Documentation

[reference](docstrings/)

# source code

[sorokin.engineer/aios3](https://github.com/andgineer/garmin-dayly)
