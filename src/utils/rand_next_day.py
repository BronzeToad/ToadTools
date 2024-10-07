from datetime import datetime, timedelta
from random import randint
from typing import Optional, Union

from src.utils.toad_logger import ToadLogger, LogLevel

frog = ToadLogger("utils.rand_next_day", level=LogLevel.DEBUG)

DEFAULT_START_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_MIN_DAYS = 1
DEFAULT_MAX_DAYS = 7


def generate_next_day(
    start_date: Optional[Union[datetime, str]] = None,
    min_days: int = DEFAULT_MIN_DAYS,
    max_days: int = DEFAULT_MAX_DAYS,
    format_str: str = "%a, %b %d, %Y",
) -> str:
    """
    Generate a random future date string based on the given parameters.

    Args:
        start_date (Optional[Union[datetime, str]], optional): The starting date.
            If a string, it should be in the format 'YYYY-MM-DD'.
            Defaults to None, which uses the current date.
        min_days (int, optional): Minimum number of days to add. Defaults to DEFAULT_MIN_DAYS.
        max_days (int, optional): Maximum number of days to add. Defaults to DEFAULT_MAX_DAYS.
        format_str (str, optional): The format string for the output date.
            Defaults to "%a, %b %d, %Y".

    Returns:
        str: A string representation of the generated future date.

    Raises:
        ValueError: If the start_date string is not in the correct format.
    """
    _default_start = datetime.now()

    if isinstance(start_date, datetime):
        start = start_date
    elif isinstance(start_date, str):
        try:
            start = datetime.strptime(start_date, DEFAULT_START_DATE_FORMAT)
        except ValueError as exc:
            frog.warning(
                f"Invalid start date format, defaulting to current date {_default_start}: {exc}"
            )
            start = _default_start
    else:
        start = _default_start

    if min_days < 1:
        frog.warning(f"Invalid min_days value '{min_days}', defaulting to 1.")
        min_days = 1

    if max_days <= min_days:
        frog.warning(
            f"Invalid max_days value '{max_days}', defaulting to min_days + 7."
        )
        max_days = min_days + 7

    random_days = randint(min_days, max_days)
    next_date = start + timedelta(days=random_days)
    next_date_str = next_date.strftime(format_str)
    return next_date_str.replace(" 0", " ")


if __name__ == "__main__":
    # Example usage
    start = "2024-10-01"
    min_days = 1
    max_days = 4

    for _ in range(15):
        next_day = generate_next_day(start, min_days, max_days)
        print(next_day)
        start = datetime.strptime(next_day, "%a, %b %d, %Y").strftime("%Y-%m-%d")
