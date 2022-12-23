"""Export Garmin data to Google Sheet."""
import os
from datetime import datetime, timedelta

import gspread
from garminconnect import Garmin

gc = gspread.service_account()

fittness = gc.open("05 Fitness").sheet1
columns_names = fittness.get("A1:J1")[0]

columns = {name: chr(ord("A") + idx) for idx, name in enumerate(columns_names)}

print(columns_names, columns)

last_date: datetime = datetime.strptime(fittness.get(columns["Date"] + "2")[0][0], "%Y-%m-%d")

print(last_date)

email = os.getenv("GARMIN_EMAIL")
password = os.getenv("GARMIN_PASSWORD")
api = Garmin(email, password)
api.login()

days_to_fill = (datetime.now() - last_date).days
print(days_to_fill)
# for day_idx in range(days_to_fill):
#     date = last_date + timedelta(days=day_idx)
#     steps_data = api.get_steps_data(date.isoformat().split("T")[0])
#     steps = sum(steps["steps"] for steps in steps_data)
#     print(date, steps)

for day_idx in range(1):
    start_date = last_date + timedelta(days=day_idx)
    stop_date = start_date  # + timedelta(days=1)

    activities = api.get_activities_by_date(start_date.isoformat(), stop_date.isoformat(), "")

    # Download activities
    for activity in activities:
        activity_id = activity["activityId"]
        # pprint(activity)
        print(
            activity["activityType"]["typeKey"],
            activity["averageHR"],
            activity["calories"],
            activity["distance"],
            activity["duration"] // 60,
            "minutes",
            activity["elevationGain"],
            activity["locationName"],
            activity["maxHR"],
            60 / activity["maxSpeed"],
            "km/h??",
            activity["startTimeLocal"],
            activity["steps"],
        )
