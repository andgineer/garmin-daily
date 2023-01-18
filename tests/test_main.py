import datetime
from unittest import mock

from click.testing import CliRunner

from garmin_daily.google_sheet import DAY_TO_ADD_WITHOUT_FORCE, SHEET_NAME_DEFAULT, Weekdays, main
from garmin_daily.version import VERSION


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
        "garmin_daily.google_sheet.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.google_sheet.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.google_sheet.open_google_sheet",
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
        "garmin_daily.google_sheet.detect_days_to_add"
    ) as mocked_detect_days_to_add, mock.patch(
        "garmin_daily.google_sheet.add_rows_from_garmin"
    ) as mocked_add_rows_from_garmin, mock.patch(
        "garmin_daily.google_sheet.open_google_sheet", return_value=(fitness, columns)
    ):
        mocked_detect_days_to_add.return_value = (start_date, days_to_add)
        result = runner.invoke(
            main,
            [
                "-g",
                "mon",
                "-g",
                "Tue",
                "--gym-duration",
                duration,
                "--gym-location",
                "Gym A",
            ],
        )
        mocked_add_rows_from_garmin.assert_called_with(
            fitness=fitness,
            columns=columns,
            start_date=start_date,
            days_to_add=days_to_add,
            gym_days=[Weekdays.MONDAY.value, Weekdays.TUESDAY.value],
            gym_duration=60,
            gym_location="Gym A",
        )
        assert result.exit_code == 0
        assert f"gym {duration} minutes training on ('Mon'," in result.output
