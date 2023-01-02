"""Export Garmin data to Google Sheet."""
import locale
import time
from datetime import date, datetime, timedelta
from enum import IntEnum
from typing import Dict, List, Optional, Tuple, Union

import click
import gspread
import gspread.exceptions
import pandas as pd

from garmin_daily import SPORT_STEP_LENGTH_KM, WALKING_SPORT, Activity, GarminDaily


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""

    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)


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
    "--gym-days",
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
    default="The classic Bulevar Oslodođenja",
    show_default=True,
    help="Gym training duration, minutes.",
    nargs=1,
)
@click.option(  # todo get locale from Google Sheet https://github.com/andgineer/garmin-daily/issues/1
    "--sheet-locale",
    "-l",
    "sheet_locale",
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
    sheet_locale: str,
    gym_location: str,
    force: bool,
) -> None:
    """Fill Google sheet with data from Garmin.

    Documentation https://andgineer.github.io/garmin-daily/
    """
    print(f"Add Garmin activities to Google Sheet '{sheet}'")
    print(f"Auto create '{gym_location}' gym {gym_duration} minutes training on {gym_weekdays}")

    fitness, columns = open_google_sheet(sheet, sheet_locale)

    fill_from_date, days_to_fill = get_first_date_to_fill(fitness, columns)
    if days_to_fill > DAY_TO_ADD_WITHOUT_FORCE and not force:
        print("\nToo many days to add.\nUse --force to confirm.")
        exit(1)

    add_rows_from_garmin(
        fitness=fitness,
        columns=columns,
        fill_from_date=fill_from_date,
        days_to_fill=days_to_fill,
        gym_days=[PCWeekdays.index(weekday) for weekday in gym_weekdays],
        gym_duration=gym_duration,
        gym_location=gym_location,
    )


def add_rows_from_garmin(
    fitness: gspread.Worksheet,
    columns: Dict[str, str],
    fill_from_date: date,
    days_to_fill: int,
    gym_days: List[int],
    gym_duration: int,
    gym_location: str,
):
    """Add activities from Garmin to the Google Sheet."""
    daily = GarminDaily()
    daily.login()

    fitness_df = load_as_pandas(fitness)

    batches_num = days_to_fill // BATCH_SIZE
    if days_to_fill % BATCH_SIZE:
        batches_num += 1
    for batch in range(batches_num):
        for day_num in range(BATCH_SIZE):
            day = fill_from_date + timedelta(days=batch * BATCH_SIZE + day_num)
            if day >= datetime.now().date():
                break
            csv = create_day_rows(
                daily=daily,
                columns=columns,
                day=day,
                gym_duration=gym_duration,
                gym_days=gym_days,
                gym_location=gym_location,
            )
            enrich_rows(fitness_df, csv)
            for row in csv:
                print("; ".join(row))
            fitness.insert_rows(csv, row=2, value_input_option="USER_ENTERED")
        time.sleep(API_DELAY)


def load_as_pandas(fitness: gspread.Worksheet) -> pd.DataFrame:
    fitness_df = pd.DataFrame(fitness.get_all_records())
    fitness_df.set_index("Date", inplace=True)
    return fitness_df


DISTANCE_IDX = 4
DATE_IDX = 3
STEPS_IDX = 5


def enrich_rows(fitness_df: pd.DataFrame, rows: List[List[str]]):
    """Add steps data from the spreadsheet."""

    def get_steps(date: str) -> int:
        """Get steps for the date like '2022-02-16'."""
        steps = fitness_df[(fitness_df.index == date)]["Steps"]
        steps = steps[steps != ""]
        return steps[steps > 0].values[0]

    for row in rows:
        no_steps_distance = "=0*"
        steps_correction = "=0"
        if row[DISTANCE_IDX].startswith(no_steps_distance):
            # Garmin did not return data for the day
            # try to look in the table
            manually_entered_steps = str(get_steps(row[DATE_IDX]))
            if row[STEPS_IDX].startswith(steps_correction):
                manually_entered_steps = f"{manually_entered_steps}{row[STEPS_IDX][len(steps_correction):]}"
                row[STEPS_IDX] = f"={manually_entered_steps}"
            else:
                # no correction formula
                row[STEPS_IDX] = manually_entered_steps
            row[DISTANCE_IDX] = f"=({manually_entered_steps})*{row[DISTANCE_IDX][len(no_steps_distance):]}"


def get_first_date_to_fill(
    fitness: gspread.Worksheet, columns: Dict[str, str]
) -> Tuple[date, int]:
    """Get last filled date and calculate date interval to fill.

    Returns (start_date, days_to_fill)
    """
    sheet_name = fitness.spreadsheet.title
    date_cell = fitness.acell(columns["Date"] + "2").value
    if not date_cell:
        print(
            f"\nCannot find last filled date in Google Sheet '{sheet_name}'.'{fitness.title}', cell {columns['Date']}2"
        )
        exit(1)
    try:
        last_date = datetime.strptime(date_cell, "%Y-%m-%d").date()
    except ValueError as e:
        print(
            f"\nWrong date string in Google Sheet '{sheet_name}'.'{fitness.title}', cell {columns['Date']}2:\n{e}"
        )
        exit(1)
    print("Last filled date", last_date)
    fill_from_date = last_date + timedelta(days=1)
    days_to_fill = (datetime.now().date() - fill_from_date).days
    print("Days to fill", days_to_fill)
    return fill_from_date, days_to_fill


def open_google_sheet(sheet: str, locale_string: str) -> Tuple[gspread.Worksheet, Dict[str, str]]:
    """Open Google Sheet.

    Return worksheet and columns map (title: id)
    """
    gc = gspread.service_account()
    try:
        worksheet = gc.open(sheet).sheet1
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"\nGoogle sheet '{sheet}' not found.")
        exit(1)
    locale.setlocale(locale.LC_NUMERIC, locale_string)

    columns_names = worksheet.get("A1:M1")[0]
    columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}
    return worksheet, columns


def create_day_rows(
    daily: GarminDaily,
    columns: Dict[str, str],
    day: date,
    gym_duration: int,
    gym_days: List[int],
    gym_location: str,
) -> List[List[str]]:
    """Sheet rows for the day.

    todo use column titles https://github.com/andgineer/garmin-daily/issues/2
    """
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
    day_rows: List[List[Optional[Union[str, int, float]]]] = [
        [
            activity.location_name,
            activity.sport,
            round(activity.duration / 60) if activity.duration else "",
            day.strftime("%Y-%m-%d"),
            round(activity.distance / 1000, 2)
            if activity.distance
            else f"={activity.steps}*{SPORT_STEP_LENGTH_KM[activity.sport]:.2n}"
            if activity.sport in SPORT_STEP_LENGTH_KM
            else "",
            f"={activity.steps}-{activity.non_walking_steps}"
            if activity.non_walking_steps
            else "",
            activity.comment,
            week_num(day),
            round(activity.duration / 60 / 60, 1) if activity.duration else 0,
            sheet_week_day(day),
            round(gday.hr_rest, 1) if activity.sport == WALKING_SPORT and gday.hr_rest else "",
            round(gday.sleep_time, 1)
            if activity.sport == WALKING_SPORT and gday.sleep_time
            else "",
            gday.vo2max if activity.sport == WALKING_SPORT and gday.vo2max else "",
        ]
        for activity in gday.activities
    ]
    return [localized_csv_raw(row) for row in day_rows]


def localized_csv_raw(row: List[Optional[Union[str, int, float]]]) -> List[str]:
    """Convert fields to the Google Sheet locale specific string representation."""
    return [f"{val:n}" if isinstance(val, float) else str(val) for val in row]


if __name__ == "__main__":
    main()
