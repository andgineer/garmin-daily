"""Export Garmin data to Google Sheet."""
from datetime import date, datetime
from pprint import pprint

import gspread

from garmin_daily import GarminDaily


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
    day = daily[date(2022, 12, 28)]
    # day = daily[date(2021, 6, 23)]
    pprint(day.activities)
    print(f"{day.min_hr=} {day.max_hr=} {day.rest_hr=} {day.average_hr=}")
    print(
        f"{day.sleep_time=} {day.sleep_deep_time=} {day.sleep_light_time=} {day.sleep_rem_time=}"
    )
    print(f"{day.vo2max=}")


if __name__ == "__main__":
    main()
