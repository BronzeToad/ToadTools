from datetime import timedelta
from enum import Enum
from typing import Optional

from src.utils.toad_logger import ToadLogger

frog = ToadLogger("reddit.models.time_period")


class TimePeriod(str, Enum):
    """Valid time periods for stats collection.

    Attributes:
        DAY: One day period.
        WEEK: One week period.
        MONTH: 30-day period.
        YEAR: 365-day period.
        ALL: All-time period.
    """

    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = "all"

    def to_timedelta(self) -> Optional[timedelta]:
        """Convert time period to a timedelta for filtering.

        Returns:
            Optional[timedelta]: The corresponding timedelta, or None for the ALL period.
        """
        time_map = {
            TimePeriod.DAY: timedelta(days=1),
            TimePeriod.WEEK: timedelta(weeks=1),
            TimePeriod.MONTH: timedelta(days=30),
            TimePeriod.YEAR: timedelta(days=365),
            TimePeriod.ALL: None,  # ALL period corresponds to no time limit
        }
        delta = time_map.get(self)
        frog.debug(f"Converted TimePeriod '{self.value}' to timedelta: {delta}")
        return delta


if __name__ == "__main__":
    frog.setLevel("DEBUG")
    periods = [
        TimePeriod.DAY,
        TimePeriod.WEEK,
        TimePeriod.MONTH,
        TimePeriod.YEAR,
        TimePeriod.ALL,
    ]
    for period in periods:
        delta = period.to_timedelta()
        print(f"{period.value.capitalize()} period corresponds to timedelta: {delta}")
