from datetime import date, datetime, timedelta
from unittest.mock import MagicMock

import pytest

from garmin_daily import Activity
from garmin_daily.google_sheet import create_day_rows, detect_days_to_add


def test_detect_days_to_add_no_date():
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": None})()
    columns = {
        "Date": "-date-cell-ref-",
    }
    with pytest.raises(SystemExit) as exc:
        detect_days_to_add(sheet_mock, columns)
    assert exc.value.code == 1


def test_detect_days_to_add_wrong_date():
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": "-invalid-date-"})()
    columns = {
        "Date": "-date-cell-ref-",
    }
    with pytest.raises(SystemExit) as exc:
        detect_days_to_add(sheet_mock, columns)
    assert exc.value.code == 1


def test_detect_days_to_add_all_filled():
    today = datetime.now().strftime("%Y-%m-%d")
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": today})()
    columns = {
        "Date": "-date-cell-ref-",
    }
    start, length = detect_days_to_add(sheet_mock, columns)
    assert start == datetime.now().date() + timedelta(days=1)
    assert length == 0


def test_detect_days_to_add():
    today = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": today})()
    columns = {
        "Date": "-date-cell-ref-",
    }
    start, length = detect_days_to_add(sheet_mock, columns)
    assert start == (datetime.now() - timedelta(days=1)).date()
    assert length == 1


def test_create_day_rows():
    mock_garmin_daily = MagicMock()

    class MockDay:
        activities = [
            Activity(distance=100, activity_type="running", location_name="1", duration=1100),
            Activity(distance=200, activity_type="elliptical", location_name="2", duration=2200),
            Activity(distance=300, activity_type="cycling", location_name="3", duration=3300),
            Activity(
                distance=400, activity_type="skate_skiing_ws", location_name="4", duration=4400
            ),
        ]

    mock_garmin_daily.__getitem__ = MagicMock(return_value=MockDay())
    columns = {"Date": "A"}
    day = date(2023, 1, 1)
    location = "fake"
    rows = create_day_rows(
        mock_garmin_daily,
        columns,
        day,
        gym_duration=30,
        gym_days=[day.weekday()],
        gym_location=location,
    )
    import pprint

    pprint.pprint(rows)
    assert rows == [
        ["1", "None", "18", "2023-01-01", "0.1", "", "None", "520", "0.3", "7", "", "", ""],
        ["2", "None", "37", "2023-01-01", "0.2", "", "None", "520", "0.6", "7", "", "", ""],
        ["3", "None", "55", "2023-01-01", "0.3", "", "None", "520", "0.9", "7", "", "", ""],
        ["4", "None", "73", "2023-01-01", "0.4", "", "None", "520", "1.2", "7", "", "", ""],
        ["fake", "Gym", "30", "2023-01-01", "", "", "", "520", "0.5", "7", "", "", ""],
    ]
