"""Garmin data aggregated daily."""
import os
from datetime import date
from typing import Any, Dict, List

from garminconnect import Garmin, GarminConnectConnectionError

MAX_LOGIN_RETRY = 5

ACTIVITY_STEPS_CORRECTIONS = {
    # km / step - we use it to calculate distance by steps.
    # also we calculate "wrong" steps that were false detected in activities like roller skiing
    # - we have to decrease the day activity by this steps number because
    # this is not real "steps" you walk
    "roller skiing": 0.0015,
    "running": 0.00089,
}

KM_IN_STEP = 0.00085  # in walking
KM_IN_MINUTE = 0.14

SPORT_DETECTION: Dict[str, Any] = {
    "running": "Running",
    "elliptical": "Ellipse",
    "skate_skiing_ws": [
        {"Skiing": {}},
        {"Roller skiing": {}},  # locationName=Петербург, startTimeLocal>=2021-4-17, <=2021.11.16
    ],
    "-unknown-": "Unknown",
}

ACTIVITY_PATH_DELIMITER = "/"
ACTIVITY_FIELDS = [
    f"activityType{ACTIVITY_PATH_DELIMITER}typeKey",  # skate_skiing_ws, 'elliptical', 'running'
    "averageHR",
    "calories",
    "distance",
    "duration",  # float seconds
    "minutes",
    "elevationGain",
    "locationName",
    "maxHR",
    "maxSpeed",  # km/h??
    "startTimeLocal",
    "steps",
]


class Activity:
    """Garmin activity."""

    def __init__(self, activity_dict: Dict[str, Any]):
        """Init."""
        for field_path in ACTIVITY_FIELDS:
            if ACTIVITY_PATH_DELIMITER in field_path:
                # process one level only for simplicity
                field_name = field_path.split(ACTIVITY_PATH_DELIMITER)[0]
                val = activity_dict[field_name][field_path.split(ACTIVITY_PATH_DELIMITER)[1]]
            else:
                field_name = field_path
                val = activity_dict.get(field_name)
            setattr(self, field_name, val)

        self.sport = self.detect_sport()
        if self.sport in ACTIVITY_STEPS_CORRECTIONS:
            self.correction_steps = (
                self.distance  # pylint: disable=no-member
                // ACTIVITY_STEPS_CORRECTIONS[self.sport]
            )  # pylint: disable=no-member
        else:
            self.correction_steps = 0

    def detect_sport(self) -> str:
        """Detect sport."""
        if self.activityType in SPORT_DETECTION:  # pylint: disable=no-member
            return SPORT_DETECTION[self.activityType]  # pylint: disable=no-member
        return SPORT_DETECTION["-unknown-"]

    def __repr__(self) -> str:
        """Show object."""
        return f"<{self.__class__.__name__} {self.__dict__.items()}>"


class GarminDay:  # pylint: disable=too-few-public-methods
    """Aggregate one day Garmin data."""

    def __init__(self, api: Garmin, day: date) -> None:
        """Set useful Garmin day fields as attributes."""
        self.api = api
        self.date = day
        self.date_str = self.date.isoformat().split("T")[0]
        # self.total_steps = self.get_steps()
        self.activities = self.aggregate_activities()

    def get_steps(self) -> int:
        """Summarize steps for the day."""
        steps_data = self.api.get_steps_data(self.date_str)
        return sum(steps["steps"] for steps in steps_data)

    def get_activities(self) -> List[Dict[str, Any]]:
        """Get activities."""
        return self.api.get_activities_by_date(self.date_str, self.date_str, "")

    def aggregate_activities(self) -> Dict[str, Any]:
        """Aggregate."""
        activities_raw = self.get_activities()
        activities = {}
        for activity_dict in activities_raw:
            activity = Activity(activity_dict)
            activities[activity.activityType] = activity  # pylint: disable=no-member
        return activities


class GarminDaily:  # pylint: disable=too-few-public-methods
    """Aggregate activities daily."""

    def __init__(self):
        """Init."""
        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")
        self.api = Garmin(email, password)

    def login(self):
        """Login."""
        retry_num = MAX_LOGIN_RETRY
        while retry_num > 0:
            try:
                self.api.login()
            except GarminConnectConnectionError as exception:
                if "Forbidden url: https://sso.garmin.com/sso/signin" in str(exception):
                    # Garmin Connect login often fail this way
                    retry_num -= 1
                    print("Login retry")
                else:
                    raise

    def __getitem__(self, day: date) -> GarminDay:
        """Get aggregated day."""
        return GarminDay(self.api, day)
