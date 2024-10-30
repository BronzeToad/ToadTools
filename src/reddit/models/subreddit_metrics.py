from datetime import datetime
from typing import Union

from pydantic import BaseModel, Field, field_validator

from src.utils.toad_logger import ToadLogger

frog = ToadLogger(__name__)


class SubredditMetrics(BaseModel):
    """Core metrics for a subreddit.

    Attributes:
        subscribers (int): Number of subscribers to the subreddit.
        active_users (int): Number of currently active users.
        created_at (datetime): Datetime when the subreddit was created.
    """

    subscribers: int = Field(default=0, ge=0)
    active_users: int = Field(default=0, ge=0)
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def validate_created_at(cls, v: Union[int, datetime]) -> datetime:
        """Convert timestamp to datetime if necessary.

        Args:
            v (Union[int, datetime]): Unix timestamp or datetime object.

        Returns:
            datetime: Validated datetime object.
        """
        frog.debug(f"Validating 'created_at' with value: {v}")
        result = datetime.fromtimestamp(v) if isinstance(v, int) else v
        frog.debug(f"'created_at' converted to datetime: {result}")
        return result


if __name__ == "__main__":
    frog.setLevel("DEBUG")
    # Test with integer timestamp
    metrics_int = SubredditMetrics(
        subscribers=10000,
        active_users=500,
        created_at=1609459200,  # Corresponds to 2021-01-01 00:00:00 UTC
    )
    print("Metrics with integer timestamp:")
    print(metrics_int)

    # Test with datetime object
    metrics_dt = SubredditMetrics(
        subscribers=15000, active_users=800, created_at=datetime(2022, 1, 1)
    )
    print("\nMetrics with datetime object:")
    print(metrics_dt)
