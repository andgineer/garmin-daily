# garmin-dayly

Fill Google Sheets with data from Garmin Connect.

Also contains bonus script to export goodreads books to markdown, I used it to have my book reviews inside Obsidian.

Honestly this is just repo for my home small automation.

## Goodreads export to markdown files

If you want to import your book reviews for example to Obsidian, all you need it to convert goodreads export CSV
to markdown files.

How to create goodreads export see in https://www.goodreads.com/review/import

In 2022 they declare it to be removed by August, but at least at the end of 2022 it still works.

I included simple script into this package to convert goodreads CSV to markdown.

Just install the package

    pip install garmin-dayly

It will install script `goodreads_csv_to_markdown`.

    $> goodreads_csv_to_markdown --help

    Usage: goodreads_csv_to_markdown [OPTIONS] [CSV_FILE] [MARKDOWN_FOLDER]

      Convert reviews and authors from goodreads export CSV file to markdown
      files.

      For example you can create nice structure in Obsidian.

      How to create goodreads export see in
      https://www.goodreads.com/review/import In 2022 they declare it to be
      removed by August, but at least at the end of 2022 it still works.

      csv_file: Goodreads export file

      markdown_folder: Folder where we create markdown files exported from
      goodreads CSV

    Options:
      --help  Show this message and exit.

## Fill Google Sheet from Garmin Connect

### Set up Google Sheets credentials for the lib
Get Google credentials for Google Sheet as explained in [gspread:Using Service Account](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)
Place it to `~/.config/gspread/service_account.json`.

Do not forget to grant access to you sheets for this service emails.

# Docstrings documentation

Documentation generated from source code.

[reference](docstrings/)

# source code

[sorokin.engineer/aios3](https://github.com/andgineer/garmin-dayly)
