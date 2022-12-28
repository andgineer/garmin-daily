"""Garmin data aggregated daily."""
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Tuple

import urllib3.exceptions
from garminconnect import Garmin
from requests.adapters import HTTPAdapter, Retry

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


MAX_LOGIN_RETRY = 5

SPORT_STEPS_CORRECTIONS = {
    # km / step - we use it to calculate distance by steps.
    # also we calculate "wrong" steps that were false detected in activities like roller skiing
    # - we have to decrease the day activity by this steps number because
    # this is not real "steps" you walk
    "Roller skiing": 0.0015,
    "Skiing": 0.0015,  # I calculated it for roller skiing hope it's the same for skiing
    "Running": 0.00089,
}

KM_IN_STEP = 0.00085  # in walking
KM_IN_MINUTE = 0.14

SPORT_DETECTION: Dict[str, Any] = {
    "running": "Running",
    "elliptical": "Ellipse",
    "cycling": "Bicycle",
    "skate_skiing_ws": {
        "Skiing": {},
        "Roller skiing": {},  # startTimeLocal>=2021-4-17, <=2021.11.16
    },
    "-unknown-": "Unknown",
}

ACTIVITY_PATH_DELIMITER = "/"
ACTIVITY_FIELDS = {  # Garmin activity filed names translation to Activity attributes
    "activity_type": f"activityType{ACTIVITY_PATH_DELIMITER}typeKey",
    "average_hr": "averageHR",
    "calories": "calories",
    "distance": "distance",
    "duration": "duration",
    "elevation_gain": "elevationGain",
    "location_name": "locationName",
    "max_hr": "maxHR",
    "max_speed": "maxSpeed",
    "start_time": "startTimeLocal",
    "steps": "steps",
}


@dataclass
class Activity:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """Garmin activity."""

    activity_type: str
    average_hr: float
    calories: float
    distance: float
    duration: float  # float seconds
    elevation_gain: float
    location_name: str
    max_hr: float
    max_speed: float  # km/h??
    start_time: str
    steps: int
    correction_steps: Optional[int] = None
    sport: Optional[str] = None

    @classmethod
    def init_from_garmin_activity(cls, garmin_activity: Dict[str, Any]) -> "Activity":
        """Create Activity object from Garmin Connect activity fields."""
        fields = {}
        for field_name, field_path in ACTIVITY_FIELDS.items():
            if ACTIVITY_PATH_DELIMITER in field_path:
                # process one level only for simplicity
                field_path_1 = field_path.split(ACTIVITY_PATH_DELIMITER)[0]
                if isinstance(garmin_activity[field_path_1], str):
                    val = garmin_activity[field_path_1]
                else:
                    val = garmin_activity[field_path_1][
                        field_path.split(ACTIVITY_PATH_DELIMITER)[1]
                    ]
            else:
                val = garmin_activity.get(field_path)
            fields[field_name] = val
        return Activity(**fields)

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

    def detect_sport(self, activity: Activity) -> Tuple[str, bool]:
        """Detect sport.

        Return (sport, separate)
        """
        if activity.activity_type in SPORT_DETECTION:  # pylint: disable=no-member
            separate = activity.distance > 8000 and activity.activity_type == "cycling"
            # todo differentiate sport by season if isinstance is dict
            return SPORT_DETECTION[activity.activity_type], separate  # pylint: disable=no-member
        return SPORT_DETECTION["-unknown-"], True

    def get_steps(self) -> int:
        """Summarize steps for the day."""
        steps_data = self.api.get_steps_data(self.date_str)
        return sum(steps["steps"] for steps in steps_data)

    def get_activities(self) -> List[Dict[str, Any]]:
        """Get activities."""
        return self.api.get_activities_by_date(self.date_str, self.date_str, "")  # type: ignore

    def aggregate_activities(self) -> Dict[str, Activity]:
        """Aggregate."""
        garmin_activities = self.get_activities()
        activities: Dict[str, List[Activity]] = defaultdict(list)
        for garmin_activity in garmin_activities:
            activity = Activity.init_from_garmin_activity(garmin_activity)
            sport, separate = self.detect_sport(activity)
            if separate:
                sport = f"{sport} {activity.start_time}"
            activities[sport].append(activity)
        aggregated: Dict[
            str, Activity
        ] = {}  # aggregate activities with same name and nearly same intensity
        for activity_name, activity_list in activities.items():
            activity = Activity(
                activity_type=activity_list[0].activity_type,
                average_hr=sum(a.average_hr for a in activity_list) / len(activity_list),
                calories=sum(a.calories for a in activity_list),
                distance=sum(a.distance for a in activity_list),
                duration=sum(a.duration for a in activity_list),
                elevation_gain=sum(a.elevation_gain for a in activity_list),
                location_name=activity_list[0].location_name,
                max_hr=max(a.max_hr for a in activity_list),
                max_speed=max(a.max_speed for a in activity_list),
                start_time=min(a.start_time for a in activity_list),
                steps=sum(0 if a.steps is None else a.steps for a in activity_list),
                sport=activity_name.split(" ")[0],
            )
            if activity.sport in SPORT_STEPS_CORRECTIONS:
                # if for the activity we know exact steps number we do not have to estimate
                activity.correction_steps = activity.steps or int(
                    activity.distance / 1000 // SPORT_STEPS_CORRECTIONS[activity.sport]
                )
            else:
                activity.correction_steps = 0
            aggregated[activity_name] = activity
        return aggregated


class GarminDaily:  # pylint: disable=too-few-public-methods
    """Aggregate activities daily."""

    def __init__(self) -> None:
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

    def login(self) -> None:
        """Login."""
        self.api.login()

    def __getitem__(self, day: date) -> GarminDay:
        """Get aggregated day."""
        return GarminDay(self.api, day)
