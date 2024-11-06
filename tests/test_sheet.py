from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from garmin_daily import Activity
from garmin_daily.columns_mapper import ColumnsMapper, GarminCol
from garmin_daily.location_mapper import LocationMapper
from garmin_daily.google_sheet import (
    BATCH_SIZE,
    add_rows_from_garmin,
    create_day_rows,
    detect_days_to_add,
    open_google_sheet,
    search_missed_steps_in_sheet,
)


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
    days_ago_last_filled = 5
    days_to_fill = days_ago_last_filled - 1  # we do not fill today because it's non-complete day
    last_filled_date_str = (datetime.now() - timedelta(days=days_ago_last_filled)).strftime(
        "%Y-%m-%d"
    )
    first_date_to_fill = (datetime.now() - timedelta(days=days_to_fill)).date()
    sheet_mock = MagicMock()
    sheet_mock.acell = lambda x: type("CellMock", (object,), {"value": last_filled_date_str})()
    start, length = detect_days_to_add(sheet_mock, ColumnsMapper(header_row[0]))
    assert start == first_date_to_fill
    assert length == days_to_fill


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
    gym_duration = 30
    location_mapper = LocationMapper([("running", "Park")], "fake")

    rows = create_day_rows(
        mock_garmin_daily,
        day,
        gym_duration=gym_duration,
        gym_days=[day.weekday()],
        location_mapper=location_mapper,
    )
    print(rows)
    assert rows == [
        {
            GarminCol.LOCATION: "Park",
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


def test_open_google_sheet():
    sheet_name = "-fake-"
    header_row = ("fake1,fake2",)
    with patch("garmin_daily.google_sheet.gspread") as mock_gspread, patch(
        "garmin_daily.google_sheet.locale"
    ) as mock_locale, patch("garmin_daily.google_sheet.ColumnsMapper") as mock_mapper:
        mock_session = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()
        mock_worksheet.get = MagicMock(return_value=header_row)
        mock_gspread.service_account = MagicMock(return_value=mock_session)
        mock_session.open = MagicMock(return_value=mock_spreadsheet)
        mock_spreadsheet.sheet1 = mock_worksheet
        open_google_sheet(sheet_name)

    mock_gspread.service_account.assert_called()
    mock_session.open.assert_called_with(sheet_name)
    mock_locale.setlocale.assert_called_with(mock_locale.LC_NUMERIC, mock_spreadsheet.locale)
    mock_mapper.assert_called_with(header_row[0])


def test_add_rows_from_garmin():
    mock_worksheet = MagicMock()
    mock_mapper = MagicMock()
    day_of_month = 2  # BATCH_SIZE * 2 + day_of_month should be valid day number
    start_date = date(2021, 1, day_of_month)
    days_to_add = 2  # less that BATCH_SIZE
    date_after_last = date(2021, 1, day_of_month + days_to_add)
    gym_days = [0, 2]
    gym_duration = 31
    location_mapper = LocationMapper([("running", "Park")], "fake")

    with patch("garmin_daily.google_sheet.GarminDaily") as mock_garmin_daily, patch(
        "garmin_daily.google_sheet.create_day_rows"
    ) as mock_create_day_rows, patch(
        "garmin_daily.google_sheet.search_missed_steps_in_sheet"
    ) as mock_search_missed_steps_in_sheet, patch(
        "garmin_daily.google_sheet.time.sleep"
    ) as mock_sleep, patch(
        "garmin_daily.google_sheet.fitness_df"
    ) as mock_fitness_df:
        with freeze_time(date_after_last):
            add_rows_from_garmin(
                fitness=mock_worksheet,
                columns=mock_mapper,
                start_date=start_date,
                days_to_add=days_to_add,
                gym_days=gym_days,
                gym_duration=gym_duration,
                location_mapper=location_mapper,
            )
        mock_sleep.assert_not_called()
        mock_garmin_daily.assert_called_once()
        mock_fitness_df.assert_not_called()
        assert mock_search_missed_steps_in_sheet.call_count == days_to_add
        assert mock_create_day_rows.call_count == days_to_add

        # not fixed
        mock_sleep.reset_mock()
        mock_search_missed_steps_in_sheet.reset_mock()
        mock_garmin_daily.reset_mock()
        mock_create_day_rows.reset_mock()

        batch_number = 2
        days_to_add = BATCH_SIZE * batch_number + 1
        date_after_last = date(2021, 1, day_of_month + days_to_add)
        with freeze_time(date_after_last):
            add_rows_from_garmin(
                fitness=mock_worksheet,
                columns=mock_mapper,
                start_date=start_date,
                days_to_add=days_to_add,
                gym_days=gym_days,
                gym_duration=gym_duration,
                location_mapper=location_mapper,
            )
        assert mock_sleep.call_count == batch_number
        mock_garmin_daily.assert_called_once()
        assert mock_search_missed_steps_in_sheet.call_count == days_to_add
        assert mock_create_day_rows.call_count == days_to_add


def test_search_missed_steps_in_sheet():
    def mock_idx(column_id):
        return {
            GarminCol.DISTANCE: 0,
            GarminCol.DATE: 1,
            GarminCol.STEPS: 2,
        }[column_id]

    fitness = MagicMock()
    columns = MagicMock()
    columns.idx = mock_idx
    # setup test data
    rows = [["=0*0.0001", "2022-02-16", "=0-400"], ["=0*0.0002", "2022-02-17", "=0-500"]]

    # mock the get_steps function to return a value of 10
    with patch("garmin_daily.google_sheet.fitness_df") as mock_fitness_df:
        mock_fitness_df.return_value = pd.DataFrame(
            [
                (100, "2022-02-16"),
                (200, "2022-02-17"),
            ],
            columns=["Steps", "Date"],
        ).set_index("Date", inplace=False)
        # call the function
        search_missed_steps_in_sheet(fitness, rows, columns)
        print(rows)

        # assert that the steps column was updated with the value of 10
        assert rows[0][columns.idx(GarminCol.STEPS)] == "=100-400"
        assert rows[1][columns.idx(GarminCol.STEPS)] == "=200-500"

        # assert that the distance column was updated with the value of 10 * 0.0007
        assert rows[0][columns.idx(GarminCol.DISTANCE)] == "=(100-400)*0.0001"
        assert rows[1][columns.idx(GarminCol.DISTANCE)] == "=(200-500)*0.0002"


def test_location_mapper():
    # Test basic location mapping
    mapper = LocationMapper([("running", "Park"), ("cycling", "Track")], "Default Gym")
    assert mapper.get_location("running", "original") == "Park"
    assert mapper.get_location("cycling activity", "original") == "Track"
    assert mapper.get_location("swimming", "original") == "original"
    assert mapper.get_gym_location() == "Default Gym"

    # Test case insensitivity
    mapper = LocationMapper([("RuNNing", "Park")], "Gym")
    assert mapper.get_location("Running", "original") == "Park"
    assert mapper.get_location("RUNNING", "original") == "Park"

    # Test gym location in mappings
    mapper = LocationMapper([("gym", "Special Gym")], None)
    assert mapper.get_gym_location() == "Special Gym"
    assert mapper.get_location("Gym Training", "original") == "Special Gym"


def test_location_mapper_conflicts():
    # Test gym location conflict between --gym-location and locations
    with pytest.raises(ValueError) as exc:
        LocationMapper([("gym", "Special Gym")], "Default Gym")
    assert "Gym location defined multiple times" in str(exc.value)

    # Test multiple gym patterns in locations
    with pytest.raises(ValueError) as exc:
        LocationMapper([
            ("gym", "Gym 1"),
            ("gym.*exercise", "Gym 2")
        ], None)
    assert "Gym location defined multiple times" in str(exc.value)

    # Test case insensitive gym pattern detection
    with pytest.raises(ValueError) as exc:
        LocationMapper([
            ("GYM", "Gym 1"),
            ("Gym", "Gym 2")
        ], None)
    assert "Gym location defined multiple times" in str(exc.value)

    # Make sure single gym location works
    try:
        LocationMapper([("gym", "Gym 1")], None)
        LocationMapper([], "Default Gym")
        LocationMapper([("GYM", "Gym 1")], None)
    except ValueError:
        pytest.fail("LocationMapper raised ValueError unexpectedly with single gym location")

def test_location_mapper_empty():
    # Test empty mappings
    mapper = LocationMapper([], None)
    assert mapper.get_location("any activity", "original") == "original"
    assert mapper.get_gym_location() is None


def test_location_mapper_pattern_matching():
    # Test pattern matching with regex
    mapper = LocationMapper([
        (r"run.*park", "Central Park"),
        (r"cycle|bike", "Bike Track"),
        (r"swim.*pool", "Swimming Pool")
    ], None)

    assert mapper.get_location("run in park", "orig") == "Central Park"
    assert mapper.get_location("running through park", "orig") == "Central Park"
    assert mapper.get_location("cycle training", "orig") == "Bike Track"
    assert mapper.get_location("bike ride", "orig") == "Bike Track"
    assert mapper.get_location("swimming in pool", "orig") == "Swimming Pool"
    assert mapper.get_location("just swimming", "orig") == "orig"