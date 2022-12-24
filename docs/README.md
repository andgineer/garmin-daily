# garmin-dayly

Fill Google Sheets with data from Garmin Connect.

Also contains bonus script to export goodreads books to markdown, I used it to have my book reviews inside Obsidian.

Honestly this is just repo for my home small automation.

## Goodreads export to markdown files

To import your book reviews from goodreads for example to Obsidian.

How to create goodreads export see in https://www.goodreads.com/review/import

In 2022 they declared it to be removed by August, but at least at the end of 2022 it still works.

Install the package

    pip install garmin-daily

It will install Linux or Windows script `goodreads-export`.

    $> goodreads-export --help

    Usage: goodreads-export [OPTIONS] [CSV_FILE]

      Convert reviews and authors from goodreads export CSV file to markdown
      files.

      For example you can create nice structure in Obsidian.

      How to create goodreads export see in
      https://www.goodreads.com/review/import In 2022 they declare it to be
      removed by August, but at least at the end of 2022 it still works.

      CSV_FILE: Goodreads export file. By default `goodreads_library_export.csv`.

    Options:
      -o, --out PATH  Folder where we put result. By default current folder.
      --help          Show this message and exit.

If we run in the folder with goodreads export file (goodreads_library_export.csv) the script without parameters

    goodreads-export

It will create in this folder subfolders `reviws`, `toread`, `authors` with the md-files.
If you copy them into Obsidian vault, the files will be inside your Obsidian knowledgebase.

## Fill Google Sheet from Garmin Connect

### Set up Google Sheets credentials for the lib
Get Google credentials for Google Sheet as explained in [gspread:Using Service Account](https://docs.gspread.org/en/latest/oauth2.html#enable-api-access-for-a-project)
Place it to `~/.config/gspread/service_account.json`.

Do not forget to grant access to you sheets for this service emails.

# Docstrings documentation

Documentation generated from source code.

[reference](docstrings/)

# source code

[sorokin.engineer/aios3](https://github.com/andgineer/garmin-daily)
