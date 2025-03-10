"""Map fields to columns using spreadsheet header row."""

from enum import Enum, IntEnum
from typing import Optional, Union


class GarminCol(IntEnum):
    """Columns of the Garmin daily data spreadsheet."""

    (
        DATE,  # activity date
        DISTANCE,  # distance if it has sense for the activity
        STEPS,  # steps if it has sense for the activity
        LOCATION,  # as in Garmin
        SPORT,  # detected from Garmin activity type - see GarminDay.detect_sport()
        DURATION,  # in minutes
        COMMENT,  # HR and speed details for sport activities / HR and sleep details for Walking
        WEEK,  # see google_sheet:week_num()
        HOURS,  # duration in hours
        WEEKDAY,  # 1 - Monday
        HR_REST,  # Rest heart rate
        SLEEP_TIME,  # in hours
        VO2_MAX,  # VO2 max
    ) = range(13)


COLUMNS_MAP: dict[str, Enum] = {
    "location": GarminCol.LOCATION,
    "sport": GarminCol.SPORT,
    "duration": GarminCol.DURATION,
    "date": GarminCol.DATE,
    "distance": GarminCol.DISTANCE,
    "steps": GarminCol.STEPS,
    "comment": GarminCol.COMMENT,
    "week": GarminCol.WEEK,
    "hours": GarminCol.HOURS,
    "week day": GarminCol.WEEKDAY,
    "day": GarminCol.WEEKDAY,
    "hr rest": GarminCol.HR_REST,
    "sleep time": GarminCol.SLEEP_TIME,
    "vo2 max": GarminCol.VO2_MAX,
}


class ColumnsMapper:
    """Map columns based on a spreadsheet header row."""

    def __init__(
        self,
        header_row: list[str],
        columns_type: type[Enum] = GarminCol,
        columns_map: Optional[dict[str, Enum]] = None,
    ) -> None:
        """Init from spreadsheet title."""
        self.columns_map = COLUMNS_MAP if columns_map is None else columns_map
        self.columns_type = columns_type
        self.column_refs = {
            self.header_to_col(name): chr(ord("A") + idx) for idx, name in enumerate(header_row)
        }
        self.column_idxs = {self.header_to_col(name): idx for idx, name in enumerate(header_row)}
        self.row_columns = self.fill_row_columns(header_row)

    def fill_row_columns(self, header_row: list[str]) -> list[Optional[Enum]]:
        """Fill list with columns as they listed in the spreadsheet header row."""
        return [self.header_to_col(header) for header in header_row]

    def header_to_col(self, header: str) -> Optional[Enum]:
        """Return column ID for the header.

        For unknown columns return None.
        """
        header_canonical = header.strip().lower()
        if header_canonical in self.columns_map:
            return self.columns_map[header_canonical]
        return None

    def map(self, fields: dict[Enum, str]) -> list[Optional[Union[str, int, float]]]:
        """Map fields to spreadsheet row.

        Unknown columns are filled with empty strings.
        """
        return [fields.get(column, "") if column is not None else "" for column in self.row_columns]

    def __getitem__(self, column: Enum) -> str:
        """Spreadsheet reference for the column."""
        return self.column_refs[column]

    def idx(self, column: Enum) -> int:
        """Index (starting from 0) for the column."""
        return self.column_idxs[column]
