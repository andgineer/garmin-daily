"""Export Garmin data to Google Sheet."""
import locale
import time
from datetime import date, datetime, timedelta
from enum import IntEnum
from typing import Dict, List, Optional, Union

import click
import gspread
import gspread.exceptions

from garmin_daily import Activity, GarminDaily


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""

    Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday = range(7)


# Weekdays based on the PC locale, not the Google Sheet locale
PCWeekdays = [date(2001, 1, i).strftime("%a") for i in range(1, 8)]

BATCH_SIZE = 7  # Add days by batches to prevent block grom Garmin API
API_DELAY = 15  # seconds to wait between batches
DAY_TO_ADD_WITHOUT_FORCE = 7  # proof against unknown bugs. to add more days use --force


def sheet_week_day(day: date) -> int:
    """Weekday number for Google Sheet.

    Monday - 1
    ...
    Sunday - 7
    """
    return day.weekday() + 1


def week_num(day: date) -> int:
    """Week number for the sheet (starting from some arbitrary date)."""
    return int(round((day - date(2013, 1, 13)).days / 7))


@click.command()
@click.option(
    "--sheet",
    "-s",
    "sheet",
    default="05 Fitness",
    show_default=True,
    help="Google sheet name to add activities from Garmin.",
    nargs=1,
)
@click.option(
    "--gym-weekdays",
    "-w",
    "gym_weekdays",
    default=[
        PCWeekdays[Weekdays.Monday.value],
        PCWeekdays[Weekdays.Tuesday.value],
        PCWeekdays[Weekdays.Friday.value],
    ],
    show_default=True,
    type=click.Choice(PCWeekdays, case_sensitive=False),
    help="Week days to add gym trainings.",
    multiple=True,
)
@click.option(
    "--gym-duration",
    "-d",
    "gym_duration",
    default=30,
    show_default=True,
    help="Gym training duration, minutes.",
    nargs=1,
)
@click.option(
    "--gym-location",
    "-l",
    "gym_location",
    default="The classic Bulevar Oslodođenja",
    show_default=True,
    help="Gym training duration, minutes.",
    nargs=1,
)
@click.option(  # todo get locale from Google Sheet https://github.com/andgineer/garmin-daily/issues/1
    "--locale",
    "-l",
    "locale_string",
    default="ru_RU",
    show_default=True,
    help="Google Sheet locale for numbers formatting.",
    nargs=1,
)
@click.option(
    "--force",
    "-f",
    "force",
    is_flag=True,
    default=False,
    show_default=True,
    help=f"Force to add more than {DAY_TO_ADD_WITHOUT_FORCE} days.",
    nargs=1,
)
def main(
    sheet: str,
    gym_weekdays: str,
    gym_duration: int,
    locale_string: str,
    gym_location: str,
    force: bool,
) -> None:
    """Fill Google sheet with data from Garmin.

    Garmin credentials should be in ??
    Garmin creds?
    """
    print(f"Add Garmin activities to Google Sheet '{sheet}'")
    print(f"Auto create '{gym_location}' gym {gym_duration} minutes training on {gym_weekdays}")

    fittness = open_google_sheet(sheet, locale_string)

    columns_names = fittness.get("A1:M1")[0]
    columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}

    fill_from_date = get_first_date_to_fill(fittness, columns, sheet)

    days_to_fill = (datetime.now().date() - fill_from_date).days
    print("Days to fill", days_to_fill)
    if days_to_fill > DAY_TO_ADD_WITHOUT_FORCE and not force:
        print("\nToo many days to add.\nUse --force to confirm.")
        exit(1)

    gym_days = [PCWeekdays.index(weekday) for weekday in gym_weekdays]

    add_rows_from_garmin(
        days_to_fill, fill_from_date, fittness, gym_days, gym_duration, gym_location
    )


def add_rows_from_garmin(
    days_to_fill: int,
    fill_from_date: date,
    fittness: gspread.Worksheet,
    gym_days: List[int],
    gym_duration: int,
    gym_location: str,
):
    """Add activities from Garmin to the Google Sheet."""
    daily = GarminDaily()
    daily.login()
    batches_num = days_to_fill // BATCH_SIZE
    if days_to_fill % BATCH_SIZE:
        batches_num += 1
    for batch in range(batches_num):
        for day_num in range(BATCH_SIZE):
            day = fill_from_date + timedelta(days=batch * BATCH_SIZE + day_num)
            if day >= datetime.now().date():
                break
            csv = create_day_rows(daily, day, gym_duration, gym_days, gym_location)
            for row in csv:
                print("; ".join(row))
            fittness.insert_rows(csv, row=2, value_input_option="USER_ENTERED")
        time.sleep(API_DELAY)


def get_first_date_to_fill(
    fittness: gspread.Worksheet, columns: Dict[str, str], sheet_name: str
) -> date:
    """Get last filled date and calculate date to fill from."""
    date_cell = fittness.get(columns["Date"] + "2")
    if not date_cell:
        print(
            f"\nCannot find last filled date in '{sheet_name}'.'{fittness.title}', cell {columns['Date']}2"
        )
        exit(1)
    try:
        last_date = datetime.strptime(date_cell[0][0], "%Y-%m-%d").date()
    except ValueError as e:
        print(
            f"\nWrong date string in '{sheet_name}'.'{fittness.title}', cell {columns['Date']}2:\n{e}"
        )
        exit(1)
    print("Last filled date", last_date)
    return last_date + timedelta(days=1)


def open_google_sheet(sheet: str, locale_string: str) -> gspread.Worksheet:
    """Open Google Sheet."""
    gc = gspread.service_account()
    try:
        worksheet = gc.open(sheet).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\nGoogle sheet '{sheet}' not found.")
        exit(1)
    locale.setlocale(locale.LC_NUMERIC, locale_string)
    return worksheet


def create_day_rows(
    daily: GarminDaily, day: date, duration: int, gym_days: List[int], gym_location: str
) -> List[List[str]]:
    """Sheet rows for the day."""
    gday = daily[day]
    if day.weekday() in gym_days:
        gday.activities.append(
            Activity(
                activity_type="Gym",
                sport="Gym",
                duration=duration * 60,
                location_name=gym_location,
                comment="",
            )
        )
    day_rows: List[List[Optional[Union[str, int, float]]]] = [
        [
            activity.location_name,
            activity.sport,
            round(activity.duration / 60) if activity.duration else "",
            day.strftime("%Y-%m-%d"),
            round(activity.distance / 1000, 2)
            if isinstance(activity.distance, float)
            else activity.distance or "",
            activity.steps or "",
            activity.comment,
            week_num(day),
            round(activity.duration / 60 / 60, 1) if activity.duration else 0,
            sheet_week_day(day),
            round(gday.hr_rest, 1),
            round(gday.sleep_time, 1) if gday.sleep_time else "",
            gday.vo2max,
        ]
        for activity in gday.activities
    ]
    return [localized_csv_raw(row) for row in day_rows]


def localized_csv_raw(row: List[Optional[Union[str, int, float]]]) -> List[str]:
    """Convert fields to CSV row.

    Use locale to format digits.
    """
    return [f"{val:n}" if isinstance(val, float) else str(val) for val in row]


if __name__ == "__main__":
    main()
