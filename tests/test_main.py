from click.testing import CliRunner

from garmin_daily.google_sheet import main
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
