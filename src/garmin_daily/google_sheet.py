"""Export Garmin data to Google Sheet."""
import locale
import sys
import time
from datetime import date, datetime, timedelta
from enum import IntEnum
from functools import lru_cache
from typing import Dict, List, Optional, Tuple, Union

import click
import gspread
import gspread.exceptions
import pandas as pd

from garmin_daily import SPORT_STEP_LENGTH_KM, WALKING_SPORT, Activity, GarminDaily
from garmin_daily.columns_mapper import ColumnsMapper, GarminCol
from garmin_daily.version import VERSION

SHEET_NAME_DEFAULT = "05 Fitness"


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""

    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)


# Weekdays based on the PC locale, not the Google Sheet locale
PCWeekdays = [date(2001, 1, i).strftime("%a") for i in range(1, 8)]

BATCH_SIZE = 7  # Add days by batches to prevent block grom Garmin API
API_DELAY = 15  # seconds to wait between batches to prevent robot protection from Garmin API
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
    default=SHEET_NAME_DEFAULT,
    show_default=True,
    help="Google sheet name to add activities from Garmin.",
    nargs=1,
)
@click.option(
    "--gym-day",
    "-g",
    "gym_weekdays",
    default=[
        PCWeekdays[Weekdays.MONDAY.value],
        PCWeekdays[Weekdays.TUESDAY.value],
        PCWeekdays[Weekdays.FRIDAY.value],
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
    default="The classic Bulevar Oslobođenja",
    show_default=True,
    help="Gym training duration, minutes.",
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
@click.option(
    "--version",
    "version",
    is_flag=True,
    default=False,
    help="Show version.",
    nargs=1,
)
def main(  # pylint: disable=too-many-arguments
    sheet: str,
    gym_weekdays: str,
    gym_duration: int,
    gym_location: str,
    force: bool,
    version: bool,
) -> None:
    """Fill Google sheet with data from Garmin.

    Documentation https://andgineer.github.io/garmin-daily/
    """
    if version:
        print(f"{VERSION}")
        sys.exit(0)

    print(f"garmin-daily {VERSION} is going to add Garmin activities to Google Sheet '{sheet}'")
    print(f"Auto create '{gym_location}' gym {gym_duration} minutes training on {gym_weekdays}")

    fitness, columns = open_google_sheet(sheet)

    start_date, days_to_add = detect_days_to_add(fitness, columns)
    if days_to_add > DAY_TO_ADD_WITHOUT_FORCE and not force:
        print(f"\nToo many days to add ({days_to_add}).\nUse --force to confirm.")
        sys.exit(1)

    if days_to_add:
        add_rows_from_garmin(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[PCWeekdays.index(weekday) for weekday in gym_weekdays],
            gym_duration=gym_duration,
            gym_location=gym_location,
        )
    else:
        print(
            f"Last filled day {start_date}. Nothing to add. Add only full days - up to yesterday."
        )


def add_rows_from_garmin(  # pylint: disable=too-many-arguments, too-many-locals
    fitness: gspread.Worksheet,
    columns: ColumnsMapper,
    start_date: date,
    days_to_add: int,
    gym_days: List[int],
    gym_duration: int,
    gym_location: str,
) -> None:
    """Add activities from Garmin to the Google Sheet."""
    daily = GarminDaily()
    daily.login()

    batches_num = days_to_add // BATCH_SIZE
    if days_to_add % BATCH_SIZE:
        batches_num += 1
    for batch in range(batches_num):
        for day_in_batch in range(BATCH_SIZE):
            day_num = batch * BATCH_SIZE + day_in_batch
            day = start_date + timedelta(days=day_num)
            if day >= datetime.now().date() or day_num >= days_to_add:
                break
            rows_fields = create_day_rows(
                daily=daily,
                day=day,
                gym_duration=gym_duration,
                gym_days=gym_days,
                gym_location=gym_location,
            )
            rows = [
                localized_csv_raw(columns.map(fields)) for fields in rows_fields  # type: ignore
            ]
            search_missed_steps_in_sheet(fitness, rows, columns)
            for row in rows:
                print("; ".join(row))
            fitness.insert_rows(rows, row=2, value_input_option="USER_ENTERED")
        if batch < batches_num - 1:  # do not pause on last iteration
            time.sleep(API_DELAY)  # pause to prevent robot protection from Garmin API


@lru_cache(maxsize=None)
def fitness_df(fitness: gspread.Worksheet) -> pd.DataFrame:
    """Load the Google Sheet as Pandas DataFrame.

    Cached so we use it as lazy load - if we do not need it we do not load it.
    """
    print("." * 20, " Reading full Google Sheet into memory for quick search ", "." * 20)
    return pd.DataFrame(fitness.get_all_records()).set_index("Date")


def search_missed_steps_in_sheet(
    fitness: gspread.Worksheet,
    rows: List[List[str]],
    columns: ColumnsMapper,
) -> None:
    """Add missed in Garmin API steps data from earlier entered in the spreadsheet.

    We need that only if we need very old data - for some reason Garmin API
    do not return steps more than for last three months.
    May be we can use some flag to get them - in the Garmin App you can see this steps
    but not from the API.
    Anyway in such situation if we already had entered steps manually in the Google Sheet
    we can find and use them.

    Just once I needed this mode so I keep it in the code.
    If you have steps from Garmin API we won't read the Google Sheet to Pandas DataFrame
    so this code won't take any resources.
    """

    def get_steps(day: str) -> int:
        """Get steps for the date like '2022-02-16'."""
        steps = fitness_df(fitness)[  # pylint: disable=unsubscriptable-object
            (fitness_df(fitness).index == day)
        ]["Steps"]
        steps = steps[steps != ""]
        steps = steps[steps > 0].values
        return steps[0] if steps.size > 0 else 0  # type: ignore

    for row in rows:
        no_steps_distance = "=0*"
        steps_correction = "=0"
        if row[columns.idx(GarminCol.DISTANCE)].startswith(no_steps_distance):
            # Garmin did not return data for the day
            # try to look in the table
            manually_entered_steps = str(get_steps(row[columns.idx(GarminCol.DATE)]))
            if row[columns.idx(GarminCol.STEPS)].startswith(steps_correction):
                manually_entered_steps = (
                    f"{manually_entered_steps}"
                    f"{row[columns.idx(GarminCol.STEPS)][len(steps_correction):]}"
                )
                row[columns.idx(GarminCol.STEPS)] = f"={manually_entered_steps}"
            else:
                # no correction formula
                row[columns.idx(GarminCol.STEPS)] = manually_entered_steps
            row[columns.idx(GarminCol.DISTANCE)] = (
                f"=({manually_entered_steps})*"
                f"{row[columns.idx(GarminCol.DISTANCE)][len(no_steps_distance):]}"
            )


def detect_days_to_add(fitness: gspread.Worksheet, columns: ColumnsMapper) -> Tuple[date, int]:
    """Get last filled date and calculate number of days to add till today.

    Returns (start_date, days_to_add)
    """
    sheet_name = fitness.spreadsheet.title
    first_data_row = 2  # after header row #1
    date_cell = fitness.acell(f"{columns[GarminCol.DATE]}{first_data_row}").value
    if not date_cell:
        print(
            f"\nCannot find last filled date in Google Sheet '{sheet_name}'.'{fitness.title}'"
            f", cell {columns[GarminCol.DATE]}{first_data_row}"
        )
        sys.exit(1)
    try:
        last_date = datetime.strptime(date_cell, "%Y-%m-%d").date()
    except ValueError as exc:
        print(
            f"\nWrong date string in Google Sheet '{sheet_name}'.'{fitness.title}', "
            f"cell {columns[GarminCol.DATE]}{first_data_row}:\n{exc}"
        )
        sys.exit(1)
    print("Last filled date", last_date)
    start_date = last_date + timedelta(days=1)
    days_to_add = (datetime.now().date() - start_date).days
    days_to_add = max(days_to_add, 0)
    print("Days to fill", days_to_add)
    return start_date, days_to_add


def open_google_sheet(sheet: str) -> Tuple[gspread.Worksheet, ColumnsMapper]:
    """Open Google Sheet.

    Return worksheet and columns map.
    Also set current locale from the spreadsheet so it will affect %n formatting.
    """
    gspread_client = gspread.service_account()
    try:
        spreadsheet = gspread_client.open(sheet)
        worksheet = spreadsheet.sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\nGoogle sheet '{sheet}' not found.")
        sys.exit(1)
    spreadsheet_locale = spreadsheet.locale
    try:
        locale.setlocale(locale.LC_NUMERIC, spreadsheet_locale)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error using the spreadsheet locale '{spreadsheet_locale}':\n{exc}")
    mapper = ColumnsMapper(worksheet.get("A1:M1")[0])
    return worksheet, mapper


def create_day_rows(  # pylint: disable=too-many-arguments
    daily: GarminDaily,
    day: date,
    gym_duration: int,
    gym_days: List[int],
    gym_location: str,
) -> List[Dict[GarminCol, Optional[Union[str, int, float]]]]:
    """Sheet rows for the day."""
    gday = daily[day]
    if day.weekday() in gym_days:
        gday.activities.append(
            Activity(
                activity_type="Gym",
                sport="Gym",
                duration=gym_duration * 60,
                location_name=gym_location,
                comment="",
            )
        )
    rows_fields: List[Dict[GarminCol, Optional[Union[str, int, float]]]] = [
        {
            GarminCol.LOCATION: activity.location_name,
            GarminCol.SPORT: activity.sport,
            GarminCol.DURATION: round(activity.duration / 60) if activity.duration else "",
            GarminCol.DATE: day.strftime("%Y-%m-%d"),
            GarminCol.DISTANCE: round(activity.distance / 1000, 2)
            if activity.distance
            else (
                f"=({activity.steps}"
                f"-{activity.non_walking_steps if activity.non_walking_steps else 0})"
                f"*{SPORT_STEP_LENGTH_KM[activity.sport]:.2n}"
            )
            if activity.sport in SPORT_STEP_LENGTH_KM
            else "",
            GarminCol.STEPS: f"={activity.steps}-{activity.non_walking_steps}"
            if activity.non_walking_steps
            else f"={activity.steps}"
            if activity.sport == WALKING_SPORT
            else "",
            GarminCol.COMMENT: activity.comment,
            GarminCol.WEEK: week_num(day),
            GarminCol.HOURS: round(activity.duration / 60 / 60, 1) if activity.duration else 0,
            GarminCol.WEEKDAY: sheet_week_day(day),
            GarminCol.HR_REST: round(gday.hr_rest, 1)
            if activity.sport == WALKING_SPORT and gday.hr_rest
            else "",
            GarminCol.SLEEP_TIME: round(gday.sleep_time, 1)
            if activity.sport == WALKING_SPORT and gday.sleep_time
            else "",
            GarminCol.VO2_MAX: gday.vo2max
            if activity.sport == WALKING_SPORT and gday.vo2max
            else "",
        }
        for activity in gday.activities
    ]
    return rows_fields


def localized_csv_raw(row: List[Optional[Union[str, int, float]]]) -> List[str]:
    """Convert fields to the Google Sheet locale specific string representation."""
    return [f"{val:n}" if isinstance(val, float) else str(val) for val in row]


if __name__ == "__main__":  # pragma: no cover
    main()  # pylint: disable=no-value-for-parameter
