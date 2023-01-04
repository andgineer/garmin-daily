from unittest.mock import MagicMock
from garmin_daily import GarminDay, Activity
from datetime import date


def test_get_hr():
    """Test that hr_max is set to the correct value."""
    get_heart_rates_response = {
        "maxHeartRate": 150,
        "minHeartRate": 50,
        "restingHeartRate": 70,
        "heartRateValues": [
            (1595304800, 60),
            (1595308000, 65),
            (1595311200, 70),
            (1595314400, 75),
            (1595317600, 80),
        ],
    }
    api = MagicMock()
    api.get_heart_rates = MagicMock(return_value=get_heart_rates_response)
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    assert garmin_day.hr_max == 150
    assert garmin_day.hr_min == 50
    assert garmin_day.hr_rest == 70
    assert garmin_day.hr_average == 70


def test_detect_sport(garmin_activity_data):
    """Test that the detect_sport correctly maps activity types to sport types."""
    api = MagicMock()
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    activity = Activity.init_from_garmin_activity(garmin_activity_data[0])
    sport, separate = garmin_day.detect_sport(activity)
    assert sport == garmin_activity_data[1]["sport"]
    assert separate == garmin_activity_data[1]["separate"]

