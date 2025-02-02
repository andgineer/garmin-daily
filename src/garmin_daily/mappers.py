"""Maps activities to locations based on pattern matching."""

import re
from typing import List, Optional, Tuple

GYM_PATTERN = "gym"


class LocationMapper:
    """Maps activities to locations based on pattern matching."""

    def __init__(
        self,
        mappings: List[Tuple[str, str]],
        gym_location: Optional[str] = None,
        is_default_gym_location: bool = False,
    ) -> None:
        """Initialize with list of (pattern, location) tuples."""
        # First find all gym locations
        gym_locations = []
        if gym_location and not is_default_gym_location:
            gym_locations.append(("--gym-location parameter", gym_location))

        for pattern, location in mappings:
            if GYM_PATTERN in pattern.lower():
                gym_locations.append((f"locations pattern '{pattern}'", location))

        if len(gym_locations) > 1:
            locations_str = "\n".join(
                f"  - {source}: {location}" for source, location in gym_locations
            )
            raise ValueError(
                f"Gym location defined multiple times:\n{locations_str}\n"
                f"Please use either --gym-location "
                f"or define gym in --locations parameter, not both."
            )

        self.gym_location = gym_locations[0][1] if gym_locations else gym_location

        # Now compile patterns
        self.mappings = [
            (re.compile(pattern, re.IGNORECASE), location) for pattern, location in mappings
        ]

    def get_location(self, activity_name: str, default_location: str) -> str:
        """Get location for activity based on matching rules."""
        for pattern, location in self.mappings:
            if pattern.search(activity_name):
                return location
        return default_location

    def get_gym_location(self) -> Optional[str]:
        """Return configured gym location."""
        return self.gym_location


class ActivityMapper:  # pylint: disable=too-few-public-methods
    """Maps activity names based on regex patterns."""

    def __init__(self, activity_mappings: List[Tuple[str, str]]):
        """Initialize with list of (pattern, new_name) tuples."""
        self.mappings = [
            (re.compile(pattern, re.IGNORECASE), new_name)
            for pattern, new_name in activity_mappings
        ]

    def get_activity_name(self, activity: str | None) -> str | None:
        """Return mapped activity name if pattern matches, otherwise return original."""
        for pattern, new_name in self.mappings:
            if isinstance(activity, str) and pattern.search(activity):
                return new_name
        return activity
