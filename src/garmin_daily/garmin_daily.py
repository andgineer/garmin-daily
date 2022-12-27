"""Garmin data aggregated daily."""
import os
from datetime import date, datetime
from typing import Any, Dict, List

from garminconnect import Garmin, GarminConnectConnectionError
from requests.adapters import HTTPAdapter, Retry

MAX_LOGIN_RETRY = 5

ACTIVITY_STEPS_CORRECTIONS = {
    # km / step - we use it to calculate distance by steps.
    # also we calculate "wrong" steps that were false detected in activities like roller skiing
    # - we have to decrease the day activity by this steps number because
    # this is not real "steps" you walk
    "skate_skiing_ws": 0.0015,  # I calculated it for roller skiing but I believe it's the same for skiing
    "running": 0.00089,
}

KM_IN_STEP = 0.00085  # in walking
KM_IN_MINUTE = 0.14

SPORT_DETECTION: Dict[str, Any] = {
    "running": "Running",
    "elliptical": "Ellipse",
    "cycling": "Bicycle",
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
    "elevationGain",
    "locationName",
    "maxHR",
    "maxSpeed",  # km/h??
    "startTimeLocal",
    "steps",
]


class Activity:
    """Garmin activity."""

    def __init__(self, **activity_dict: Dict[str, Any]):
        """Init."""
        for field_path in ACTIVITY_FIELDS:
            if ACTIVITY_PATH_DELIMITER in field_path:
                # process one level only for simplicity
                field_name = field_path.split(ACTIVITY_PATH_DELIMITER)[0]
                if isinstance(activity_dict[field_name], str):
                    val = activity_dict[field_name]
                else:
                    val = activity_dict[field_name][field_path.split(ACTIVITY_PATH_DELIMITER)[1]]
            else:
                field_name = field_path
                val = activity_dict.get(field_name)
            setattr(self, field_name, val)

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
        self.total_steps = self.get_steps()
        self.activities = self.aggregate_activities()

    def detect_sport(self, activity: Activity) -> (str, bool):
        """Detect sport.
        Return (sport, separate)"""
        if activity.activityType in SPORT_DETECTION:  # pylint: disable=no-member
            separate = activity.distance > 8000 and activity.activityType == "cycling"
            return SPORT_DETECTION[activity.activityType], separate  # pylint: disable=no-member
        return SPORT_DETECTION["-unknown-"], True

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
            activity = Activity(**activity_dict)
            sport, separate = self.detect_sport(activity)
            if separate:
                sport = f"{sport} {activity.startTimeLocal}"
            if sport not in activities:
                activities[sport] = []
            activities[sport].append(activity)  # pylint: disable=no-member
        for activity in activities:
            activities[activity] = Activity(
                activityType=activities[activity][0].activityType,
                averageHR=sum(activity.averageHR for activity in activities[activity]) / len(activities[activity]),
                calories=sum(activity.calories for activity in activities[activity]),
                distance=sum(activity.distance for activity in activities[activity]),
                duration=sum(activity.duration for activity in activities[activity]),
                elevationGain=sum(activity.elevationGain for activity in activities[activity]),
                locationName=activities[activity][0].locationName,
                maxHR=max(activity.maxHR for activity in activities[activity]),
                maxSpeed=max(activity.maxSpeed for activity in activities[activity]),
                startTimeLocal=min(activity.startTimeLocal for activity in activities[activity]),
                steps=sum(0 if activity.steps is None else activity.steps for activity in activities[activity]),
            )
            if activities[activity] in ACTIVITY_STEPS_CORRECTIONS:
                activities[activity].correction_steps = (
                        activities[activity].distance  # pylint: disable=no-member
                        // ACTIVITY_STEPS_CORRECTIONS[activities[activity].sport]
                )  # pylint: disable=no-member
            else:
                activities[activity].correction_steps = 0
        return activities


class GarminDaily:  # pylint: disable=too-few-public-methods
    """Aggregate activities daily."""

    def __init__(self):
        """Init."""
        email = os.getenv("GARMIN_EMAIL")
        password = os.getenv("GARMIN_PASSWORD")
        self.api = Garmin(email, password)
        self.api.session.verify = False
        retries = Retry(
            total=5,
            backoff_factor=3,  # retry in [0, 6, 12, 24, 48] seconds
            status_forcelist=[403],
        )
        self.api.session.mount("https://", HTTPAdapter(max_retries=retries))

    def login(self):
        """Login."""
        self.api.login()

    def __getitem__(self, day: date) -> GarminDay:
        """Get aggregated day."""
        return GarminDay(self.api, day)
