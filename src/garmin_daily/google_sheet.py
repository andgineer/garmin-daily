"""Export Garmin data to Google Sheet."""
from datetime import date, datetime
from enum import IntEnum
from pprint import pprint

import gspread

from garmin_daily import Activity, GarminDaily

Weekdays = IntEnum("Weekdays", "mon tue wed thu fri sat sun", start=0)


GYM_DAYS = [Weekdays.mon.value, Weekdays.tue.value, Weekdays.fri.value]
GYM_LOCATION = "The classic Bulevar Oslodođenja"


def main() -> None:
    """Debug."""
    gc = gspread.service_account()

    fittness = gc.open("05 Fitness").sheet1
    columns_names = fittness.get("A1:J1")[0]

    columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}

    print(columns_names, columns)

    last_date: datetime = datetime.strptime(fittness.get(columns["Date"] + "2")[0][0], "%Y-%m-%d")

    print(last_date)

    days_to_fill = (datetime.now() - last_date).days
    print(days_to_fill)

    # 27.01.22 - ski 'locationName': 'Всеволожский район',
    # 9.03.22 - ellipse  'locationName': None,
    # 10.04.23 run 'locationName': 'Novi Sad',
    # 14.10.21 roller ski,  'locationName': 'Петербург',
    # The classic bulevar Oslodođenja
    # Самоизоляция

    # for start_date in [date(2022, 1, 27), date(2022, 3, 9), date(2022, 4, 23), date(2021, 10, 14)]:
    #     # start_date = last_date + timedelta(days=day_idx)

    daily = GarminDaily()
    daily.login()

    day = date(2022, 12, 28)
    gday = daily[day]
    # day = daily[date(2021, 6, 23)]
    if day.weekday() in GYM_DAYS:
        gday.activities.append(
            Activity(
                activity_type="Gym", sport="Gym", duration=30 * 60, location_name=GYM_LOCATION
            )
        )
    pprint(gday.activities)
    print(f"{gday.total_steps=}")
    print(f"{gday.min_hr=} {gday.max_hr=} {gday.rest_hr=} {gday.average_hr=}")
    print(
        f"{gday.sleep_time=} {gday.sleep_deep_time=} {gday.sleep_light_time=} {gday.sleep_rem_time=}"
    )
    print(f"{gday.vo2max=}")


if __name__ == "__main__":
    main()
