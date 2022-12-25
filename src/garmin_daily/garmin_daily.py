"""Garmin data aggregated daily."""
from datetime import datetime
from typing import Any, Dict

ACTIVITY_GROUPS: Dict[str, Any] = {
    "Walking": {},
    "Running": {},
    "Skiing": {},
    "Roller skiing": {},
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


class GarminDay:  # pylint: disable=too-few-public-methods
    """Aggregated day."""

    def __init__(self, day: Dict[str, Any]) -> None:
        """Set useful Garmin day fields as attributes."""
        for field_path in ACTIVITY_FIELDS:
            if ACTIVITY_PATH_DELIMITER in field_path:
                # process one level only for simplicity
                field_name = field_path.split(ACTIVITY_PATH_DELIMITER)[0]
                val = day[field_name][field_path.split(ACTIVITY_PATH_DELIMITER)[1]]
            else:
                field_name = field_path
                val = day[field_name]
            setattr(self, field_name, val)


class GarminDaily:  # pylint: disable=too-few-public-methods
    """Aggregate activities daily."""

    def __getitem__(self, date: datetime) -> GarminDay:
        """Get aggregated day."""
        return GarminDay({})
