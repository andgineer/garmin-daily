"""Export Garmin data to Google Sheet."""
from datetime import date, datetime
from enum import IntEnum
from typing import List, Union
import locale

import gspread

from garmin_daily import Activity, GarminDaily


class Weekdays(IntEnum):
    """Weekdays for datetime.weekday."""
    Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday = range(7)


GYM_DAYS = [Weekdays.Monday.value, Weekdays.Tuesday.value, Weekdays.Friday.value]
GYM_LOCATION = "The classic Bulevar Oslodođenja"


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
    # set decimal point delimiters as in my Goog Sheets
    locale.setlocale(locale.LC_NUMERIC, 'ru_RU')
    print(locale.str(1.1))

    gc = gspread.service_account()

    fittness = gc.open("05 Fitness").sheet1

    columns_names = fittness.get("A1:M1")[0]
    columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}
    print(columns_names)

    last_date: datetime = datetime.strptime(fittness.get(columns["Date"] + "2")[0][0], "%Y-%m-%d")
    print("Last filled date", last_date)

    days_to_fill = (datetime.now() - last_date).days
    print("Days to fill", days_to_fill)

    # for start_date in [date(2022, 1, 27), date(2022, 3, 9), date(2022, 4, 23), date(2021, 10, 14)]:
    #     # start_date = last_date + timedelta(days=day_idx)

    daily = GarminDaily()
    daily.login()

    create_day_rows(daily, date(2022, 12, 25))  # date(2021, 6, 23)


def create_day_rows(daily: GarminDaily, day: date):
    """Sheet rows for the day."""
    gday = daily[day]
    if day.weekday() in GYM_DAYS:
        gday.activities.append(
            Activity(
                activity_type="Gym", sport="Gym", duration=30 * 60, location_name=GYM_LOCATION
            )
        )
    day_rows: List[List[Union[str, int, float]]] = [
        [
            activity.location_name,
            activity.sport,
            round(activity.duration / 60) if activity.duration else "",
            day.strftime("%Y-%m-%d"),
            round(activity.distance / 1000, 2) if activity.distance else "",
            activity.steps or "",
            activity.comment,
            week_num(day),
            round(activity.duration / 60 / 60, 1) if activity.duration else 0,
            sheet_week_day(day),
            round(gday.hr_rest, 1),
            round(gday.sleep_time, 1),
            gday.vo2max,
        ]
        for activity in gday.activities
    ]
    for row in day_rows:
        print(localized_csv_raw(row))


def localized_csv_raw(row: List[Union[str, int, float]], field_separator: str = ";") -> str:
    """Convert fields to CSV row.

    Use locale to format digits.
    """
    return field_separator.join([val if isinstance(val, str) else f"{val:n}" for val in row])


if __name__ == "__main__":
    main()
