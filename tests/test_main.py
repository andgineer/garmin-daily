import datetime
from unittest import mock

from click.testing import CliRunner

from garmin_daily.main import DAY_TO_ADD_WITHOUT_FORCE, SHEET_NAME_DEFAULT, Weekdays, main
from garmin_daily.mappers import LocationMapper, ActivityMapper
from garmin_daily.version import VERSION


class LocationMapperMatcher:
    def __init__(self, mappings, gym_location):
        self.mappings = mappings
        self.gym_location = gym_location

    def __eq__(self, other):
        if not isinstance(other, LocationMapper):
            return False
        # Compare pattern strings and locations
        actual_mappings = [(p.pattern, l) for p, l in other.mappings]
        return (actual_mappings == self.mappings and
                self.gym_location == other.gym_location)

    def __repr__(self):
        return f"LocationMapper(mappings={self.mappings}, gym_location='{self.gym_location}')"


class ActivityMapperMatcher:
    def __init__(self, mappings):
        self.mappings = mappings

    def __eq__(self, other):
        if not isinstance(other, ActivityMapper):
            return False
        actual_mappings = [(p.pattern, n) for p, n in other.mappings]
        return actual_mappings == self.mappings

    def __repr__(self):
        return f"ActivityMapperMatcher(mappings={self.mappings})"


def test_main_version():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            # "",  # sheet
            # "--sheet-locale", "",
            # "--gym-duration", 30,
            # "--gym-day", "mon",
            # "--gym-location", "",
            # "--force"
            "--version",
        ],
    )
    assert result.exit_code == 0
    assert VERSION in result.output


def test_too_many_days_to_add():
    runner = CliRunner()
    with mock.patch(
        "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet",
        return_value=(mock.MagicMock(), mock.MagicMock()),
    ) as mocked_open_google_sheet:
        mocked_detect_days_to_add.return_value = (
            datetime.date(2022, 1, 1),
            DAY_TO_ADD_WITHOUT_FORCE + 1,
        )
        result = runner.invoke(main, [])
        assert "Too many days to add" in result.output
        mocked_add_rows_from_garmin.assert_not_called()
        mocked_open_google_sheet.assert_called_with(SHEET_NAME_DEFAULT)


def test_gym_training_added():
    runner = CliRunner()
    duration = "60"
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE


    with mock.patch(
        "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)
        result = runner.invoke(
            main,
            [
                "-g", "mon",
                "-g", "Tue",
                "--gym-duration", duration,
                "--gym-location", "Gym A",
            ],
        )
        expected_mapper = LocationMapperMatcher([], "Gym A")
        activity_mapper = ActivityMapperMatcher([])
        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[Weekdays.MONDAY.value, Weekdays.TUESDAY.value],
            gym_duration=60,
            location_mapper=expected_mapper,
            activity_mapper=activity_mapper,
        )
        assert result.exit_code == 0
        assert f"gym {duration} minutes training on ['Mon'," in result.output


def test_locations_parameter():
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE

    with mock.patch(
            "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)

        # Test with locations parameter
        result = runner.invoke(
            main,
            [
                "--locations", "running=Park",
                "--locations", "cycling=Track",
                "--gym-location", "Gym A",
                "--gym-day", "",  # Override default gym days with empty value
            ],
            catch_exceptions=False
        )

        assert result.exit_code == 0, f"Command failed with output: {result.output}"

        expected_mapper = LocationMapperMatcher(
            [("running", "Park"), ("cycling", "Track")],
            "Gym A"
        )
        activity_mapper = ActivityMapperMatcher([])
        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[],  # Empty list because we passed empty --gym-day
            gym_duration=30,  # Default duration
            location_mapper=expected_mapper,
            activity_mapper=activity_mapper,
        )

def test_locations_with_default_gym_days():
    """Test locations parameter with default gym days."""
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE


    with mock.patch(
        "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)

        # Test with locations parameter and default gym days
        result = runner.invoke(
            main,
            [
                "--locations", "running=Park",
                "--locations", "cycling=Track",
                "--gym-location",
                "Gym A",
            ],
            catch_exceptions=False
        )

        assert result.exit_code == 0, f"Command failed with output: {result.output}"

        expected_mapper = LocationMapperMatcher(
            [("running", "Park"), ("cycling", "Track")],
            "Gym A"
        )
        activity_mapper = ActivityMapperMatcher([])
        # Default gym days are Monday, Tuesday, Friday (0, 1, 4)
        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[0, 1, 4],  # Default gym days
            gym_duration=30,  # Default duration
            location_mapper=expected_mapper,
            activity_mapper=activity_mapper,
        )

def test_locations_with_gym():
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE

    with mock.patch(
            "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)

        # Test with gym in locations
        result = runner.invoke(
            main,
            [
                "--locations", "running=Park",
                "--locations", "gym=Special Gym",
                "--gym-day", "",
            ],
        )
        assert result.exit_code == 0, f"Command failed with output: {result.output}"

        expected_mapper = LocationMapperMatcher(
            [("running", "Park"), ("gym", "Special Gym")],
            "Special Gym"
        )
        expected_activity_mapper = ActivityMapperMatcher([])
        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[],
            gym_duration=30,
            location_mapper=expected_mapper,
            activity_mapper=expected_activity_mapper,
        )
        assert result.exit_code == 0


def test_locations_gym_conflict():
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "--locations", "running=Park",
            "--locations", "gym=Special Gym",
            "--gym-location", "Another Gym",
        ],
    )
    assert result.exit_code == 1
    assert "Gym location defined multiple times" in result.output
    assert "locations pattern 'gym': Special Gym" in result.output
    assert "--gym-location parameter: Another Gym" in result.output


def test_gym_location_default_ignored():
    """Test that default gym location is ignored when gym is in locations."""
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE

    with mock.patch(
            "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)
        result = runner.invoke(
            main,
            [
                "--locations", "running=Park",
                "--locations", "gym=Special Gym",
                # Not specifying --gym-location should use default "No Limit Gym"
                # but it should be ignored because gym is in locations
            ]
        )
    assert result.exit_code == 0
    assert "Special Gym" in result.output
    assert "No Limit Gym" not in result.output


def test_rename_parameter():
    """Test activity rename parameter."""
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE


    with mock.patch(
            "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)

        # Test with rename parameter
        result = runner.invoke(
            main,
            [
                "--rename", "trail=Roller skiing",
                "--rename", "running=Jogging",
                "--gym-day", "",  # Override default gym days
            ],
            catch_exceptions=False
        )

        assert result.exit_code == 0, f"Command failed with output: {result.output}"

        expected_activity_mapper = ActivityMapperMatcher([
            ("trail", "Roller skiing"),
            ("running", "Jogging")
        ])

        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[],
            gym_duration=30,
            location_mapper=mock.ANY,  # We don't care about location mapper in this test
            activity_mapper=expected_activity_mapper
        )


def test_rename_invalid_format():
    """Test activity rename with invalid format."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["--rename", "invalid-format"]  # Missing '=' separator
    )
    assert result.exit_code == 1
    assert "Invalid rename format" in result.output


def test_rename_with_locations():
    """Test activity rename working together with locations."""
    runner = CliRunner()
    fitness = mock.MagicMock()
    columns = mock.MagicMock()
    start_date = datetime.date(2022, 1, 1)
    days_to_add = DAY_TO_ADD_WITHOUT_FORCE

    with mock.patch(
            "garmin_daily.main.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.main.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.main.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)

        result = runner.invoke(
            main,
            [
                "--rename", "trail=Roller skiing",
                "--locations", "running=Park",
                "--gym-day", "",
            ],
            catch_exceptions=False
        )

        assert result.exit_code == 0

        assert "Activity rename mappings:" in result.output
        assert "trail -> Roller skiing" in result.output
        assert "Activity location mappings:" in result.output
        assert "running -> Park" in result.output

        # Verify both mappers were used in the call
        call_kwargs = mocked_add_rows_from_garmin.call_args[1]
        assert isinstance(call_kwargs['activity_mapper'], ActivityMapper)
        assert isinstance(call_kwargs['location_mapper'], LocationMapper)