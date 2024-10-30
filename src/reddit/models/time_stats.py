from datetime import datetime
from typing import Optional, List, Union
from statistics import mean, median

from praw.models import Submission
from pydantic import BaseModel, Field, field_validator

from reddit.models.time_period import TimePeriod
from src.utils.toad_logger import ToadLogger

frog = ToadLogger(__name__)


class TimeStats(BaseModel):
    """Container for time-based statistics.

    Attributes:
        period (TimePeriod): Time period for the statistics.
        total_posts (int): Total number of posts in the period.
        avg_upvotes (float): Average number of upvotes per post.
        median_upvotes (float): Median number of upvotes per post.
        max_upvotes (int): Maximum number of upvotes on any post.
        posts_per_day (float): Average number of posts per day.
        oldest_post_date (Optional[datetime]): Date of the oldest post in the period.
        newest_post_date (Optional[datetime]): Date of the newest post in the period.
    """

    period: TimePeriod
    total_posts: int = Field(ge=0)
    avg_upvotes: float = Field(ge=0)
    median_upvotes: float = Field(ge=0)
    max_upvotes: int = Field(ge=0)
    posts_per_day: float = Field(ge=0)
    oldest_post_date: Optional[datetime] = None
    newest_post_date: Optional[datetime] = None

    @field_validator("oldest_post_date", "newest_post_date", mode="before")
    @classmethod
    def validate_dates(cls, v: Union[int, float, datetime, None]) -> Optional[datetime]:
        """Convert timestamp to datetime if necessary.

        Args:
            v (Union[int, float, datetime, None]): Unix timestamp, datetime object, or None.

        Returns:
            Optional[datetime]: Validated datetime object or None.
        """
        frog.debug(f"Validating date value: {v}")
        if isinstance(v, (int, float)):
            result = datetime.fromtimestamp(v)
            frog.debug(f"Converted timestamp {v} to datetime: {result}")
            return result
        frog.debug(f"Date value is already a datetime or None: {v}")
        return v

    @classmethod
    def from_posts(cls, posts: List[Submission], period: TimePeriod) -> "TimeStats":
        """Create a TimeStats instance from a list of posts.

        Args:
            posts (List[Submission]): List of Reddit submissions.
            period (TimePeriod): Time period for the statistics.

        Returns:
            TimeStats: Calculated statistics for the given posts.
        """
        frog.debug(f"Computing TimeStats for period: {period.value}")
        if not posts:
            frog.debug("No posts provided. Returning default TimeStats with zeroed values.")
            return cls(
                period=period,
                total_posts=0,
                avg_upvotes=0.0,
                median_upvotes=0.0,
                max_upvotes=0,
                posts_per_day=0.0,
            )

        upvotes = [post.score for post in posts]
        timestamps = [post.created_utc for post in posts]
        oldest_time = min(timestamps)
        newest_time = max(timestamps)
        time_span = (newest_time - oldest_time) / 86400  # Convert to days
        frog.debug(f"Calculated time_span (days): {time_span}")

        stats = cls(
            period=period,
            total_posts=len(posts),
            avg_upvotes=mean(upvotes),
            median_upvotes=median(upvotes),
            max_upvotes=max(upvotes),
            posts_per_day=len(posts) / (time_span if time_span > 0 else 1),
            oldest_post_date=oldest_time,
            newest_post_date=newest_time,
        )
        frog.debug(f"Generated TimeStats: {stats}")
        return stats

    class Config:
        frozen = True  # Make the model immutable


if __name__ == "__main__":
    frog.setLevel("DEBUG")
    # Create a list of mock submissions for testing
    from collections import namedtuple
    MockSubmission = namedtuple('MockSubmission', ['score', 'created_utc'])
    import time

    # Current time in Unix timestamp
    now = time.time()

    # Create mock posts with varying scores and timestamps
    posts = [
        MockSubmission(score=10, created_utc=now - 10000),
        MockSubmission(score=20, created_utc=now - 5000),
        MockSubmission(score=30, created_utc=now - 1000),
    ]

    period = TimePeriod.DAY
    time_stats = TimeStats.from_posts(posts, period)
    print(f"TimeStats for period '{period.value}':")
    print(f"Total Posts: {time_stats.total_posts}")
    print(f"Average Upvotes: {time_stats.avg_upvotes}")
    print(f"Median Upvotes: {time_stats.median_upvotes}")
    print(f"Max Upvotes: {time_stats.max_upvotes}")
    print(f"Posts per Day: {time_stats.posts_per_day}")
    print(f"Oldest Post Date: {time_stats.oldest_post_date}")
    print(f"Newest Post Date: {time_stats.newest_post_date}")