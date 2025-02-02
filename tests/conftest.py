import json
import pathlib
from pathlib import Path

import pytest

from garmin_daily.columns_mapper import GarminCol


def _get_repo_root_dir() -> str:
    """
    :return: path to the project folder.
    `tests/` should be in the same folder and this file should be in the root of `tests/`.
    """
    return str(Path(__file__).parent.parent)


ROOT_DIR = _get_repo_root_dir()
RESOURCES = pathlib.Path(f"{ROOT_DIR}/tests/resources")

garmin_ativities_marked_data = [
    {
        "api_responce": {
            "activityType": {"typeKey": "running"},
            "duration": 3600,
            "calories": 250,
            "distance": 10,
            "elevationGain": 50,
            "maxHR": 170,
            "averageHR": 150,
            "startTimeLocal": "2022-01-01T09:00:00",
            "steps": 5000,
            "movingDuration": 3500,
        },
        "test_metadata": {
            "sport": "Running",
            "separate": False,
            "estimated_steps": 11,
            "str": "<Activity(activity_type=running, location_name=None, duration=3600, average_hr=150, calories=250, distance=10, elevation_gain=50, max_hr=170, max_speed=None, average_speed=None, start_time=2022-01-01T09:00:00, steps=5000, moving_duration=3500, non_walking_steps=None, sport=None, comment=None>",
        },
    },
    {
        "api_responce": {
            "activityType": {"typeKey": "cycling"},
            "duration": 3600,
            "calories": 300,
            "distance": 30,
            "elevationGain": 75,
            "maxHR": 190,
            "averageHR": 170,
            "startTimeLocal": "2022-01-03T09:00:00",
            "steps": 7500,
            "movingDuration": 3500,
        },
        "test_metadata": {
            "sport": "Bicycle",
            "separate": False,
            "estimated_steps": 0,
            "str": "<Activity(activity_type=cycling, location_name=None, duration=3600, average_hr=170, calories=300, distance=30, elevation_gain=75, max_hr=190, max_speed=None, average_speed=None, start_time=2022-01-03T09:00:00, steps=7500, moving_duration=3500, non_walking_steps=None, sport=None, comment=None>",
        },
    },
    {
        "api_responce": {
            "activityType": {"typeKey": "-fake_fake-"},
            "duration": 3600,
            "calories": 250,
            "distance": 10,
            "elevationGain": 50,
            "maxHR": 170,
            "averageHR": 150,
            "startTimeLocal": "2022-01-01T09:00:00",
            "steps": 5000,
            "movingDuration": 3500,
        },
        "test_metadata": {
            "sport": "-fake Fake-",
            "separate": False,
            "estimated_steps": 0,
            "str": "<Activity(activity_type=-fake_fake-, location_name=None, duration=3600, average_hr=150, calories=250, distance=10, elevation_gain=50, max_hr=170, max_speed=None, average_speed=None, start_time=2022-01-01T09:00:00, steps=5000, moving_duration=3500, non_walking_steps=None, sport=None, comment=None>",
        },
    },
]


@pytest.fixture(scope="module", params=garmin_ativities_marked_data)
def garmin_activity_marked(request):
    return request.param["api_responce"], request.param["test_metadata"]


@pytest.fixture(scope="function")
def garmin_activities_data():
    with (RESOURCES / "activities.json").open("r", encoding="utf8") as f:
        result = json.loads(f.read())
    return result


@pytest.fixture(scope="function")
def garmin_step_data():
    with (RESOURCES / "steps.json").open("r", encoding="utf8") as f:
        result = json.loads(f.read())
    return result


@pytest.fixture(scope="function")
def garmin_sleep_data():
    with (RESOURCES / "sleep.json").open("r", encoding="utf8") as f:
        result = json.loads(f.read())
    return result


@pytest.fixture(
    scope="module",
    params=[
        (
            [
                "Location",
                "Sport",
                "Duration",
                "Date",
                "Distance",
                "Steps",
                "Comment",
                "Week",
                "Hours",
                "Week Day",
                "HR rest",
                "Sleep time",
                "VO2 max",
            ],
            {
                "idx": {GarminCol.DATE: 3, GarminCol.STEPS: 5, GarminCol.DISTANCE: 4},
                "row_columns": [
                    GarminCol.LOCATION,
                    GarminCol.SPORT,
                    GarminCol.DURATION,
                    GarminCol.DATE,
                    GarminCol.DISTANCE,
                    GarminCol.STEPS,
                    GarminCol.COMMENT,
                    GarminCol.WEEK,
                    GarminCol.HOURS,
                    GarminCol.WEEKDAY,
                    GarminCol.HR_REST,
                    GarminCol.SLEEP_TIME,
                    GarminCol.VO2_MAX,
                ],
                "row": ["", "", "-duration-", "-date-", "", "", "", "", "", "", "", "", ""],
            },
        ),
    ],
)
def header_row(request):
    return request.param
