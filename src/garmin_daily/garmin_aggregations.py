"""Garmin data aggregated daily."""

import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, Callable, Dict, List, Optional, Tuple, Union, get_type_hints

import urllib3.exceptions
from garminconnect import Garmin
from requests.adapters import HTTPAdapter, Retry

from garmin_daily.snake_to_camel import snake_to_camel

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

MAX_LOGIN_RETRY = 5

WALKING_SPORT = "Walking"
WALKING_LOCATION = "Novi Sad"

SPORT_STEP_LENGTH_KM = {
    "Roller skiing": 0.0015,
    "Skiing": 0.0015,  # I calculated it for roller skiing hope it's the same for skiing
    "Running": 0.00089,
    WALKING_SPORT: 0.00085,  # experimentally 0.14 km/min = 8.5 km/h
}

SPORT_DETECTION: Dict[str, Any] = {
    "running": "Running",
    "elliptical": "Ellipse",
    "cycling": "Bicycle",
    "skate_skiing_ws": {
        "Skiing": [
            {"from": date(2021, 4, 17), "to": date(2021, 11, 16)},
        ],
        "default": "Roller skiing",
    },
    "-unknown-": "Unknown",
}


class AggFunc(Enum):
    """Activity field aggregation function."""

    sum = sum
    max = max
    min = min
    average = "average"
    first = "first"


@dataclass()
class ActivityField:
    """Activity field description."""

    garmin_field: Optional[
        str
    ]  # the field name in Garmin Connect, None if not exists in Garmin activity
    aggregate: Union[AggFunc, Callable[[Any], Any]]  # aggregate function type or function itself


ACTIVITY_PATH_DELIMITER = "/"


@dataclass
class Activity:  # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """Garmin activity."""

    activity_type: Annotated[
        str, ActivityField(f"activityType{ACTIVITY_PATH_DELIMITER}typeKey", AggFunc.first)
    ]
    location_name: Annotated[str, ActivityField("", AggFunc.first)]
    duration: Annotated[Optional[float], ActivityField("", AggFunc.sum)]  # float seconds

    average_hr: Annotated[Optional[float], ActivityField("averageHR", AggFunc.average)] = None
    calories: Annotated[Optional[float], ActivityField("", AggFunc.sum)] = None
    distance: Annotated[Optional[Union[float, str]], ActivityField("", AggFunc.sum)] = None
    elevation_gain: Annotated[Optional[float], ActivityField("", AggFunc.sum)] = None
    max_hr: Annotated[Optional[float], ActivityField("maxHR", AggFunc.max)] = None
    max_speed: Annotated[Optional[float], ActivityField("", AggFunc.max)] = None  # km/h??
    average_speed: Annotated[Optional[float], ActivityField("", AggFunc.max)] = None
    start_time: Annotated[Optional[str], ActivityField("startTimeLocal", AggFunc.min)] = None
    steps: Annotated[Optional[int], ActivityField("", AggFunc.sum)] = None
    moving_duration: Annotated[Optional[float], ActivityField("", AggFunc.sum)] = None

    # in non-Walking activity this is steps calculated in non-walking activities for this day
    # we should subtract them from Walking activity steps to get "real" walking steps
    non_walking_steps: Annotated[Optional[int], ActivityField(None, AggFunc.sum)] = None

    sport: Annotated[Optional[str], ActivityField(None, AggFunc.first)] = None
    comment: Annotated[Optional[str], ActivityField(None, AggFunc.first)] = None

    @classmethod
    def init_from_garmin_activity(cls, garmin_activity: Dict[str, Any]) -> "Activity":
        """Create Activity object from Garmin Connect activity fields."""
        fields = {}
        descr: Dict[str, ActivityField] = {
            field: get_type_hints(Activity, include_extras=True)[field].__metadata__[0]
            for field in get_type_hints(Activity, include_extras=True)
        }
        for field_name, field_decr in descr.items():
            field_path = field_decr.garmin_field
            if field_path is None:
                continue
            if field_path == "":
                field_path = snake_to_camel(field_name)
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

    @staticmethod
    def to_km_h(garmin_speed: Optional[float]) -> Optional[float]:
        """Convert m/s to km/h and round to 2 digits after point."""
        return round(garmin_speed * 60 * 60 / 1000, 2) if garmin_speed else None

    def estimate_steps(self) -> int:
        """Estimate steps for the activity.

        Garmin do not provide steps for some activities.
        Actually it erroneously calculate steps during such activities like roller skiing.
        We have to estimate this steps to subtract them from Walking activity steps.
        """
        if self.sport in SPORT_STEP_LENGTH_KM and isinstance(self.distance, float):
            return int(self.distance / 1000 // SPORT_STEP_LENGTH_KM[self.sport])
        else:
            return 0

    def __repr__(self) -> str:
        """Show object."""
        return f"<{self.__class__.__name__} {self.__dict__.items()}>"


class GarminDay:  # pylint: disable=too-few-public-methods
    """Aggregate one day Garmin data."""

    hr_max: Optional[float] = None
    hr_min: Optional[float] = None
    hr_average: Optional[float] = None
    hr_rest: float = float()
    sleep_time: Optional[float] = None
    sleep_deep_time: Optional[float] = None
    sleep_light_time: Optional[float] = None
    sleep_rem_time: Optional[float] = None

    def __init__(self, api: Garmin, day: date) -> None:
        """Set useful Garmin day fields as attributes."""
        self.api = api
        self.date = day
        self.date_str = self.date.isoformat().split("T")[0]
        self.total_steps = self.get_steps()
        self.get_hr()
        self.get_sleep()
        self.vo2max = self.get_vo2max()
        self.activities = self.aggregate_activities()

    def get_vo2max(self) -> float:
        """Get VO2 max."""
        return self.api.get_training_status(self.date_str)["mostRecentVO2Max"]["generic"][  # type: ignore
            "vo2MaxValue"
        ]

    def get_hr(self) -> None:
        """Set HR attrs."""
        hr_data = self.api.get_heart_rates(self.date_str)
        self.hr_max = hr_data["maxHeartRate"]
        self.hr_min = hr_data["minHeartRate"]
        self.hr_rest = hr_data["restingHeartRate"]
        if hr_data["heartRateValues"] is not None:
            hr_sum = sum(hr[1] for hr in hr_data["heartRateValues"] if hr[1])
            hr_count = sum(1 for hr in hr_data["heartRateValues"] if hr[1])
            self.hr_average = hr_sum / hr_count
            # hr[1] Unix time in ms, datetime.utcfromtimestamp(hr[0] / 1000)
        else:
            self.hr_average = None

    def get_sleep(self) -> None:
        """Set sleep attrs."""
        sleep_data = self.api.get_sleep_data(self.date_str)
        if sleep_data["dailySleepDTO"]["sleepTimeSeconds"] is not None:
            self.sleep_time = sleep_data["dailySleepDTO"]["sleepTimeSeconds"] // 60 / 60
            self.sleep_deep_time = sleep_data["dailySleepDTO"]["deepSleepSeconds"] // 60 / 60
            self.sleep_light_time = sleep_data["dailySleepDTO"]["lightSleepSeconds"] // 60 / 60
            self.sleep_rem_time = sleep_data["dailySleepDTO"]["remSleepSeconds"] // 60 / 60

    def detect_sport(self, activity: Activity) -> Tuple[str, bool]:
        """Detect sport.

        Return (sport, separate)

        If the activity looks like significant one we want to see it separately.
        For example we would like to aggregate all small bicycle trips but not the big training one.
        """
        if activity.activity_type in SPORT_DETECTION:  # pylint: disable=no-member
            separate = (
                activity.distance
                and isinstance(activity.distance, int)
                and activity.distance > 8000
                and activity.activity_type == "cycling"
            )
            # todo differentiate sport by season if isinstance is dict
            return (  # type: ignore
                SPORT_DETECTION[activity.activity_type],
                separate,
            )  # pylint: disable=no-member
        return SPORT_DETECTION["-unknown-"], True

    def get_steps(self) -> int:
        """Summarize steps for the day."""
        steps_data = self.api.get_steps_data(self.date_str)
        return sum(steps["steps"] for steps in steps_data)

    def get_activities(self) -> List[Dict[str, Any]]:
        """Get activities."""
        return self.api.get_activities_by_date(self.date_str, self.date_str, "")  # type: ignore

    def aggregate_activities(self) -> List[Activity]:
        """Aggregate activities with same name and nearly same intensity."""
        garmin_activities = self.get_activities()
        activities: Dict[str, List[Activity]] = defaultdict(list)
        for garmin_activity in garmin_activities:
            activity = Activity.init_from_garmin_activity(garmin_activity)
            sport, separate = self.detect_sport(activity)
            if separate:  # do not aggregate
                sport = f"{sport} {activity.start_time}"
            if isinstance(sport, dict):
                for key, val in sport.items():
                    if isinstance(val, list):
                        for interval in val:
                            if (
                                interval["from"]
                                <= datetime.strptime(
                                    activity.start_time, "%Y-%m-%d %H:%M:%S"
                                ).date()
                                >= interval["to"]
                            ):
                                sport = key
                                break
                    if isinstance(sport, str):
                        break
                else:
                    sport = sport["default"]
            activities[sport].append(activity)
        aggregated: Dict[str, Activity] = {
            activity_name: self.aggregate_activity(activity_name, activity_list)
            for activity_name, activity_list in activities.items()
        }
        aggregated[WALKING_SPORT] = self.aggregate_walking_activity(aggregated)
        return list(aggregated.values())

    def aggregate_walking_activity(self, activities: Dict[str, Activity]) -> Activity:
        """Aggregate full day walking into single activity."""
        return Activity(
            activity_type=WALKING_SPORT,
            sport=WALKING_SPORT,
            duration=None,
            steps=self.total_steps,
            non_walking_steps=sum(
                activity.steps for activity in activities.values() if activity.steps
            ),
            location_name=WALKING_LOCATION,
            comment=self.dump_attrs(self, "hr_min", "hr_max", "hr_avg:hr_average", precision=0)
            + " "
            + self.dump_attrs(
                self,
                "sleep_deep:sleep_deep_time",
                "sleep_light:sleep_light_time",
                "sleep_rem:sleep_rem_time",
            ),
            distance=None,
        )

    @staticmethod
    def dump_float(val: Optional[float], precision: int = 1) -> str:
        """Rounded representation if float or empty."""
        if isinstance(val, float):
            val = round(val, precision)
            if precision == 0:
                val = int(val)
        return f"{val}" if val else ""

    @staticmethod
    def dump_attrs(
        obj, *attributes_names: str, func: Callable[[Any], Any] = None, precision: int = 1
    ) -> str:
        """Dump the obj's attributes as 'name=value'.

        Skip None or empty ("", 0).
        If there is ":" in the name then treat it as dump_name:attr_name
        """
        result = []
        for name in attributes_names:
            if ":" in name:
                dump_name, attr_name = name.split(":")
            else:
                dump_name = attr_name = name
            if getattr(obj, attr_name):
                val = getattr(obj, attr_name)
                if func:
                    val = func(val)
                result.append(f"{dump_name}={GarminDay.dump_float(val, precision=precision)}")
        return " ".join(result)

    @staticmethod
    def aggregate_activity(activity_name: str, activity_list: List[Activity]) -> Activity:
        """Aggregate the list of activities into one accumulative activity."""
        fields = {}
        descr: Dict[str, ActivityField] = {
            field: get_type_hints(Activity, include_extras=True)[field].__metadata__[0]
            for field in get_type_hints(Activity, include_extras=True)
        }
        for field_name, field_decr in descr.items():
            if field_decr.aggregate in [AggFunc.min, AggFunc.max, AggFunc.sum]:
                fields[field_name] = field_decr.aggregate.value(  # type: ignore
                    getattr(activity, field_name) or 0 for activity in activity_list
                )
            elif field_decr.aggregate == AggFunc.first:
                fields[field_name] = getattr(activity_list[0], field_name)
            elif field_decr.aggregate == AggFunc.average:
                num = sum(1 for activity in activity_list if getattr(activity, field_name))
                if num:
                    fields[field_name] = (
                        sum(
                            getattr(activity, field_name)
                            for activity in activity_list
                            if getattr(activity, field_name)
                        )
                        / num
                    )
                else:
                    fields[field_name] = None
        fields["sport"] = activity_name.split(" ")[0]  # just sport name without start time
        activity = Activity(**fields)
        activity.comment = (
            GarminDay.dump_attrs(
                activity,
                "speed_max:max_speed",
                "speed_avg:average_speed",
                func=Activity.to_km_h,
                precision=2,
            )
            + " "
            + GarminDay.dump_attrs(activity, "hr_max:max_hr", "hr_avg:average_hr", precision=0)
        )
        if not activity.steps:
            activity.steps = activity.estimate_steps()
        return activity


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
