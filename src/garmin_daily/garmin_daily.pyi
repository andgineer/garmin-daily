# typing. may be it would be easier just to add fields to the class but I wanted to use this new way
from typing import Optional

class Activity:
    activityType: str
    averageHR: float
    calories: float
    distance: float
    duration: float
    elevationGain: float
    locationName: str
    maxHR: float
    maxSpeed: float
    startTimeLocal: str
    steps: int
