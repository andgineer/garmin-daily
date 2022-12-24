"""Garmin data aggregated daily."""
from datetime import datetime


class GarminDay:  # pylint: disable=too-few-public-methods
    """Aggregated day."""


class GarminDaily:  # pylint: disable=too-few-public-methods
    """Aggregate activities daily."""

    def __getitem__(self, date: datetime) -> GarminDay:
        """Get aggregated day."""
        return GarminDay()
