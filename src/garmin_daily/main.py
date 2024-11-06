"""Export Garmin data to Google Sheet."""

import sys
from datetime import date
from enum import IntEnum
from typing import Tuple

import click.core as click_core
import rich_click as click

from garmin_daily.google_sheet import add_rows_from_garmin, detect_days_to_add, open_google_sheet
from garmin_daily.location_mapper import LocationMapper
from garmin_daily.version import VERSION

SHEET_NAME_DEFAULT = "05 Fitness"


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""

    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)


# Weekdays based on the PC locale, not the Google Sheet locale
PCWeekdays = [date(2001, 1, i).strftime("%a") for i in range(1, 8)]

DAY_TO_ADD_WITHOUT_FORCE = 7  # proof against unknown bugs. to add more days use --force

GYM_LOCATION_DEFAULT = "No Limit Gym"


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
    type=click.Choice(PCWeekdays + [""], case_sensitive=False),
    help="Week days to add gym trainings. Set empty to disable adding gym days.",
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
    "-y",
    "gym_location",
    default=GYM_LOCATION_DEFAULT,
    show_default=True,
    help="Gym location.",
    nargs=1,
)
@click.option(
    "--locations",
    "-l",
    "activity_locations",
    help="Activity regex pattern and location pairs (e.g. 'running=Park,cycling=Bike Path').",
    multiple=True,
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
def main(  # pylint: disable=too-many-arguments, too-many-locals
    sheet: str,
    gym_weekdays: Tuple[str, ...],
    gym_duration: int,
    gym_location: str,
    activity_locations: Tuple[str, ...],
    force: bool,
    version: bool,
) -> None:
    """Fill Google sheet with data from Garmin.

    Documentation https://andgineer.github.io/garmin-daily/en/
    """
    ctx = click.get_current_context()
    if version:
        print(f"{VERSION}")
        sys.exit(0)

    # Parse activity-location mappings
    location_mappings = []
    if activity_locations:
        try:
            for pair in activity_locations:
                pattern, location = pair.split("=", 1)  # Changed from '-' to '='
                location_mappings.append((pattern, location))
        except ValueError:
            print("Invalid locations format. Use: pattern1=location1,pattern2=location2")
            sys.exit(1)

    gym_location_param = ctx.get_parameter_source("gym_location")
    is_default_gym_location = gym_location_param is click_core.ParameterSource.DEFAULT
    try:
        location_mapper = LocationMapper(location_mappings, gym_location, is_default_gym_location)
    except ValueError as exc:
        print(exc)
        sys.exit(1)

    print(f"garmin-daily {VERSION} is going to add Garmin activities to Google Sheet '{sheet}'")
    if location_mappings:
        print("Activity location mappings:")
        for pattern, location in location_mappings:
            print(f"  {pattern} -> {location}")

    filtered_gym_weekdays = [day for day in gym_weekdays if day]
    if (
        gym_location := location_mapper.get_gym_location()  # type: ignore
        and filtered_gym_weekdays
    ):
        print(
            f"Auto create '{gym_location}' gym {gym_duration} minutes training "
            f"on {filtered_gym_weekdays}"
        )

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
            gym_days=[PCWeekdays.index(weekday) for weekday in filtered_gym_weekdays],
            gym_duration=gym_duration,
            location_mapper=location_mapper,
        )
    else:
        print(
            f"Last filled day {start_date}. Nothing to add. Add only full days - up to yesterday."
        )


if __name__ == "__main__":  # pragma: no cover
    main()  # pylint: disable=no-value-for-parameter
