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

It will install script `goodreads-export`.

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

For example if we run in the folder where we place goodreads export file (goodreads_library_export.csv)

    goodreads-export

It will create in this folder subfolders `reviws`, `toread`, `authors` with the md-files.
If you copy it for example into Obsidian vault, the files will be inside your Obsidian knowledgebase.

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
