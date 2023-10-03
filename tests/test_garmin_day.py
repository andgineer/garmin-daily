import os
from datetime import date
from unittest.mock import MagicMock, patch

from garmin_daily import Activity, ActivityField, AggFunc, GarminDaily, GarminDay


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

    get_heart_rates_response["heartRateValues"] = None
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    assert garmin_day.hr_max == 150
    assert garmin_day.hr_min == 50
    assert garmin_day.hr_rest == 70
    assert garmin_day.hr_average is None


def test_detect_sport(garmin_activity_marked):
    """Test that the detect_sport correctly maps activity types to sport types."""
    api = MagicMock()
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    activity = Activity.init_from_garmin_activity(garmin_activity_marked[0])
    sport, separate = garmin_day.detect_sport(activity)
    assert sport == garmin_activity_marked[1]["sport"]
    assert separate == garmin_activity_marked[1]["separate"]

    activity.activity_type = "-fake-"
    assert garmin_day.detect_sport(activity) == ("Unknown", True)


def test_aggregate_activities(garmin_activities_data):
    api = MagicMock()
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    garmin_day.get_activities = MagicMock(return_value=garmin_activities_data)
    garmin_day.hr_max = 136
    garmin_day.hr_min = 42
    garmin_day.hr_rest = 68
    garmin_day.hr_average = 68
    garmin_day.sleep_deep_time = 0.9166666666666666
    garmin_day.sleep_light_time = 5.6
    garmin_day.sleep_rem_time = 2.0833333333333335
    garmin_day.total_steps = 6969
    expected = [
        Activity(
            activity_type="skate_skiing_ws",
            location_name="УТЦ",
            duration=878.9879760742188,
            average_hr=132.0,
            calories=154.0,
            distance=3716.6201171875,
            elevation_gain=7.2703094482421875,
            max_hr=144.0,
            max_speed=6.289000034332275,
            average_speed=4.228000164031982,
            start_time="2023-01-03 12:14:15",
            steps=2477,
            moving_duration=779.0,
            non_walking_steps=0,
            sport="Roller skiing",
            comment="speed_max=22.64 speed_avg=15.22 hr_max=144 hr_avg=132",
        ),
        Activity(
            activity_type="skate_skiing_ws",
            location_name="УТЦ",
            duration=878.9879760742188,
            average_hr=132.0,
            calories=154.0,
            distance=3716.6201171875,
            elevation_gain=7.2703094482421875,
            max_hr=144.0,
            max_speed=6.289000034332275,
            average_speed=4.228000164031982,
            start_time="2021-04-17 12:14:15",
            steps=2477,
            moving_duration=779.0,
            non_walking_steps=0,
            sport="Skiing",
            comment="speed_max=22.64 speed_avg=15.22 hr_max=144 hr_avg=132",
        ),
        Activity(
            activity_type="cycling",
            location_name="Novi Sad",
            duration=3076.8619995117188,
            average_hr=117.75,
            calories=453.0,
            distance=10790.440063476562,
            elevation_gain=67.6540298461914,
            max_hr=146.0,
            max_speed=6.289000034332275,
            average_speed=4.228000164031982,
            start_time="2023-01-03 09:10:52",
            steps=0,
            moving_duration=2450.0,
            non_walking_steps=0,
            sport="Bicycle",
            comment="speed_max=22.64 speed_avg=15.22 hr_max=146 hr_avg=118",
        ),
        Activity(
            activity_type="cycling",
            location_name="Novi Sad",
            duration=878.9879760742188,
            average_hr=132.0,
            calories=154.0,
            distance=37016.6201171875,
            elevation_gain=7.2703094482421875,
            max_hr=144.0,
            max_speed=6.289000034332275,
            average_speed=4.228000164031982,
            start_time="2023-01-03 12:14:15",
            steps=0,
            moving_duration=779.0,
            non_walking_steps=0,
            sport="Bicycle",
            comment="speed_max=22.64 speed_avg=15.22 hr_max=144 hr_avg=132",
        ),
        Activity(
            activity_type="Walking",
            location_name="Novi Sad",
            duration=None,
            average_hr=None,
            calories=None,
            distance=None,
            elevation_gain=None,
            max_hr=None,
            max_speed=None,
            average_speed=None,
            start_time=None,
            steps=6969,
            moving_duration=None,
            non_walking_steps=4954,
            sport="Walking",
            comment="hr_min=42 hr_max=136 hr_avg=68 sleep_deep=0.9 sleep_light=5.6 sleep_rem=2.1",
        ),
    ]
    assert garmin_day.aggregate_activities() == expected


def test_get_steps(garmin_step_data):
    api = MagicMock()
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    garmin_day.api.get_steps_data = MagicMock(return_value=garmin_step_data)
    assert garmin_day.get_steps() == 6969


def test_get_sleep(garmin_sleep_data):
    api = MagicMock()
    garmin_day = GarminDay(api=api, day=date(2023, 1, 1))
    garmin_day.api.get_sleep_data = MagicMock(return_value=garmin_sleep_data)
    assert garmin_day.get_sleep() == (8.6, 0.9166666666666666, 5.6, 2.0833333333333335)

    garmin_sleep_data["dailySleepDTO"]["sleepTimeSeconds"] = None
    assert garmin_day.get_sleep() == (None, None, None, None)


def test_activity_field_aggregate_field():
    # Test sum aggregation function
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.SUM)
    activity_list = [
        Activity(distance=1, activity_type="", location_name="", duration=None),
        Activity(distance=2, activity_type="", location_name="", duration=None),
        Activity(distance=3, activity_type="", location_name="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "distance") == 6

    # Test min aggregation function
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.MIN)
    activity_list = [
        Activity(elevation_gain=10, activity_type="", location_name="", duration=None),
        Activity(elevation_gain=5, activity_type="", location_name="", duration=None),
        Activity(elevation_gain=20, activity_type="", location_name="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "elevation_gain") == 5

    # Test max aggregation function
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.MAX)
    activity_list = [
        Activity(elevation_gain=10, activity_type="", location_name="", duration=None),
        Activity(elevation_gain=5, activity_type="", location_name="", duration=None),
        Activity(elevation_gain=20, activity_type="", location_name="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "elevation_gain") == 20

    # Test first aggregation function
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.FIRST)
    activity_list = [
        Activity(location_name="Run", activity_type="", duration=None),
        Activity(location_name="Bike", activity_type="", duration=None),
        Activity(location_name="Swim", activity_type="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "location_name") == "Run"

    # Test average aggregation function
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.AVERAGE)
    activity_list = [
        Activity(distance=1, activity_type="", location_name="", duration=None),
        Activity(distance=2, activity_type="", location_name="", duration=None),
        Activity(distance=3, activity_type="", location_name="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "distance") == 2.0

    # Test average aggregation function with no values for field
    field_descr = ActivityField(garmin_field=None, aggregate=AggFunc.AVERAGE)
    activity_list = [
        Activity(distance=None, activity_type="", location_name="", duration=None),
        Activity(distance=None, activity_type="", location_name="", duration=None),
        Activity(distance=None, activity_type="", location_name="", duration=None),
    ]
    assert GarminDay.aggregate_field(activity_list, field_descr, "distance") is None


def test_garmin_day_init():
    with patch.dict(
        os.environ, {"GARMIN_EMAIL": "fake-email", "GARMIN_PASSWORD": "fake-password"}
    ), patch("garmin_daily.garmin_aggregations.Garmin") as garmin_mock:
        garmin_day = GarminDaily()
        garmin_mock.assert_called_with("fake-email", "fake-password")
        garmin_day.api.garth.sess.mount.assert_called()
