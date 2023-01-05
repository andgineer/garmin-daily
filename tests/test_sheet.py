from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from garmin_daily.google_sheet import detect_days_to_add


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
