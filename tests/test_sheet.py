from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from garmin_daily import Activity
from garmin_daily.columns_mapper import ColumnsMapper, GarminCol
from garmin_daily.google_sheet import create_day_rows, detect_days_to_add


def test_detect_days_to_add_no_date(header_row):
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": None})()
    with pytest.raises(SystemExit) as exc:
        detect_days_to_add(sheet_mock, ColumnsMapper(header_row[0]))
    assert exc.value.code == 1


def test_detect_days_to_add_wrong_date(header_row):
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": "-invalid-date-"})()
    with pytest.raises(SystemExit) as exc:
        detect_days_to_add(sheet_mock, ColumnsMapper(header_row[0]))
    assert exc.value.code == 1


def test_detect_days_to_add_all_filled(header_row):
    today = datetime.now().strftime("%Y-%m-%d")
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": today})()
    start, length = detect_days_to_add(sheet_mock, ColumnsMapper(header_row[0]))
    assert start == datetime.now().date() + timedelta(days=1)
    assert length == 0


def test_detect_days_to_add(header_row):
    today = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": today})()
    start, length = detect_days_to_add(sheet_mock, ColumnsMapper(header_row[0]))
    assert start == (datetime.now() - timedelta(days=1)).date()
    assert length == 1


def test_create_day_rows(header_row):
    mock_garmin_daily = MagicMock()

    class MockDay:
        activities = [
            Activity(
                distance=100,
                activity_type="running",
                location_name="1",
                duration=1100,
                sport="Running",
            ),
            Activity(distance=200, activity_type="elliptical", location_name="2", duration=2200),
            Activity(distance=300, activity_type="cycling", location_name="3", duration=3300),
            Activity(
                distance=400, activity_type="skate_skiing_ws", location_name="4", duration=4400
            ),
        ]

    mock_garmin_daily.__getitem__ = MagicMock(return_value=MockDay())
    day = date(2023, 1, 1)
    gym_location = "fake"
    gym_duration = 30
    rows = create_day_rows(
        mock_garmin_daily,
        day,
        gym_duration=gym_duration,
        gym_days=[day.weekday()],
        gym_location=gym_location,
    )
    print(rows)
    assert rows == [
        {
            GarminCol.LOCATION: "1",
            GarminCol.SPORT: "Running",
            GarminCol.DURATION: 18,
            GarminCol.DATE: "2023-01-01",
            GarminCol.DISTANCE: 0.1,
            GarminCol.STEPS: "",
            GarminCol.COMMENT: None,
            GarminCol.WEEK: 520,
            GarminCol.HOURS: 0.3,
            GarminCol.WEEKDAY: 7,
            GarminCol.HR_REST: "",
            GarminCol.SLEEP_TIME: "",
            GarminCol.VO2_MAX: "",
        },
        {
            GarminCol.LOCATION: "2",
            GarminCol.SPORT: None,
            GarminCol.DURATION: 37,
            GarminCol.DATE: "2023-01-01",
            GarminCol.DISTANCE: 0.2,
            GarminCol.STEPS: "",
            GarminCol.COMMENT: None,
            GarminCol.WEEK: 520,
            GarminCol.HOURS: 0.6,
            GarminCol.WEEKDAY: 7,
            GarminCol.HR_REST: "",
            GarminCol.SLEEP_TIME: "",
            GarminCol.VO2_MAX: "",
        },
        {
            GarminCol.LOCATION: "3",
            GarminCol.SPORT: None,
            GarminCol.DURATION: 55,
            GarminCol.DATE: "2023-01-01",
            GarminCol.DISTANCE: 0.3,
            GarminCol.STEPS: "",
            GarminCol.COMMENT: None,
            GarminCol.WEEK: 520,
            GarminCol.HOURS: 0.9,
            GarminCol.WEEKDAY: 7,
            GarminCol.HR_REST: "",
            GarminCol.SLEEP_TIME: "",
            GarminCol.VO2_MAX: "",
        },
        {
            GarminCol.LOCATION: "4",
            GarminCol.SPORT: None,
            GarminCol.DURATION: 73,
            GarminCol.DATE: "2023-01-01",
            GarminCol.DISTANCE: 0.4,
            GarminCol.STEPS: "",
            GarminCol.COMMENT: None,
            GarminCol.WEEK: 520,
            GarminCol.HOURS: 1.2,
            GarminCol.WEEKDAY: 7,
            GarminCol.HR_REST: "",
            GarminCol.SLEEP_TIME: "",
            GarminCol.VO2_MAX: "",
        },
        {
            GarminCol.LOCATION: "fake",
            GarminCol.SPORT: "Gym",
            GarminCol.DURATION: 30,
            GarminCol.DATE: "2023-01-01",
            GarminCol.DISTANCE: "",
            GarminCol.STEPS: "",
            GarminCol.COMMENT: "",
            GarminCol.WEEK: 520,
            GarminCol.HOURS: 0.5,
            GarminCol.WEEKDAY: 7,
            GarminCol.HR_REST: "",
            GarminCol.SLEEP_TIME: "",
            GarminCol.VO2_MAX: "",
        },
    ]
