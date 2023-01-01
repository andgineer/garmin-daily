"""Export Garmin data to Google Sheet."""
import locale
import time
from datetime import date, datetime, timedelta
from enum import IntEnum
from typing import List, Optional, Union

import gspread

from garmin_daily import Activity, GarminDaily


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""

    Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday = range(7)


GYM_DAYS = [Weekdays.Monday.value, Weekdays.Tuesday.value, Weekdays.Friday.value]
GYM_LOCATION = "The classic Bulevar Oslodođenja"
BATCH_SIZE = 7  # Add days by batches to prevent block grom Garmin API
API_DELAY = 15  # seconds to wait between batches


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


def main() -> None:
    """Debug."""
    gc = gspread.service_account()

    fittness = gc.open("05 Fitness").sheet1
    # todo get locale from Google Sheet https://github.com/andgineer/garmin-daily/issues/1
    locale.setlocale(locale.LC_NUMERIC, "ru_RU")

    columns_names = fittness.get("A1:M1")[0]
    columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}

    last_date = datetime.strptime(fittness.get(columns["Date"] + "2")[0][0], "%Y-%m-%d").date()
    print("Last filled date", last_date)
    fill_from_date = last_date + timedelta(days=1)

    days_to_fill = (datetime.now().date() - fill_from_date).days
    print("Days to fill", days_to_fill)

    daily = GarminDaily()
    daily.login()

    batches_num = days_to_fill // BATCH_SIZE
    if days_to_fill % BATCH_SIZE:
        batches_num += 1
    for batch in range(batches_num):
        for day_num in range(BATCH_SIZE):
            day = last_date + timedelta(days=batch * BATCH_SIZE + day_num)
            if day >= datetime.now().date():
                break
            csv = create_day_rows(daily, day)
            for row in csv:
                print("; ".join(row))
            fittness.insert_rows(csv, row=2, value_input_option="USER_ENTERED")
        time.sleep(API_DELAY)


def create_day_rows(daily: GarminDaily, day: date) -> List[List[str]]:
    """Sheet rows for the day."""
    gday = daily[day]
    if day.weekday() in GYM_DAYS:
        gday.activities.append(
            Activity(
                activity_type="Gym",
                sport="Gym",
                duration=30 * 60,
                location_name=GYM_LOCATION,
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


def localized_csv_raw(
    row: List[Optional[Union[str, int, float]]]
) -> List[str]:
    """Convert fields to CSV row.

    Use locale to format digits.
    """
    return [f"{val:n}" if isinstance(val, float) else str(val) for val in row]


if __name__ == "__main__":
    main()
