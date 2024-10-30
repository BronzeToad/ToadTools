from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, List, Set

import praw
import yaml
from praw.models import Subreddit, Submission

from reddit.models.subreddit_metrics import SubredditMetrics
from reddit.models.time_period import TimePeriod
from reddit.models.time_stats import TimeStats
from src.utils.toad_logger import ToadLogger

frog = ToadLogger(__name__)


class SubredditStats:
    """Reddit subreddit statistics collector.

    Attributes:
        subreddit_name (str): Name of the subreddit to analyze.
        time_periods (Optional[Set[TimePeriod]]): Set of time periods to analyze.
        config_path (Path): Path to Reddit API configuration file.
        metrics (Optional[SubredditMetrics]): Basic subreddit metrics.
        time_stats (Dict[TimePeriod, TimeStats]): Dictionary of time-based statistics by period.
    """

    def __init__(
        self,
        subreddit_name: str,
        time_periods: Optional[List[str]] = None,
        config_path: Optional[Path] = None,
    ) -> None:
        """Initialize SubredditStats.

        Args:
            subreddit_name (str): Name of the subreddit to analyze.
            time_periods (Optional[List[str]]): Optional list of time periods ("day", "week", "month", "year", "all").
            config_path (Optional[Path]): Optional path to Reddit API config file.
        """
        self.subreddit_name = subreddit_name
        self.time_periods = self._validate_time_periods(time_periods)
        self.config_path = config_path or Path(__file__).parents[1] / "config.yaml"
        self.metrics: Optional[SubredditMetrics] = None
        self.time_stats: Dict[TimePeriod, TimeStats] = {}

        self._reddit: Optional[praw.Reddit] = None
        self._subreddit: Optional[Subreddit] = None
        frog.info(f"Initialized SubredditStats for r/{subreddit_name}")

    @staticmethod
    def _validate_time_periods(
        time_periods: Optional[List[str]],
    ) -> Optional[Set[TimePeriod]]:
        """Validate and convert time period strings to TimePeriod enum.

        Args:
            time_periods (Optional[List[str]]): List of time period strings to validate.

        Returns:
            Optional[Set[TimePeriod]]: Set of valid time periods or None.
        """
        if not time_periods:
            return None

        valid_periods = set()
        for period in time_periods:
            try:
                valid_periods.add(TimePeriod(period.lower()))
            except ValueError:
                frog.warning(f"Invalid time period ignored: {period}")
        return valid_periods

    def _initialize_reddit(self) -> praw.Reddit:
        """Initialize the Reddit API client.

        Returns:
            praw.Reddit: Initialized Reddit API client.

        Raises:
            RuntimeError: If initialization fails.
        """
        try:
            with open(self.config_path, "r") as file:
                config = yaml.safe_load(file)

            reddit = praw.Reddit(
                client_id=config["reddit"]["client_id"],
                client_secret=config["reddit"]["client_secret"],
                user_agent=config["reddit"]["user_agent"],
            )
            frog.info("Successfully initialized Reddit API client")
            return reddit

        except (FileNotFoundError, KeyError, yaml.YAMLError) as e:
            frog.error(f"Failed to initialize Reddit client: {str(e)}")
            raise RuntimeError(f"Reddit client initialization failed: {str(e)}") from e

    @property
    def reddit(self) -> praw.Reddit:
        """Lazy initialization of Reddit instance.

        Returns:
            praw.Reddit: Initialized Reddit API client.
        """
        if self._reddit is None:
            self._reddit = self._initialize_reddit()
        return self._reddit

    @property
    def subreddit(self) -> Subreddit:
        """Lazy initialization of subreddit instance.

        Returns:
            Subreddit: Initialized subreddit instance.
        """
        if self._subreddit is None:
            self._subreddit = self.reddit.subreddit(self.subreddit_name)
        return self._subreddit

    def _collect_posts(self, limit: Optional[timedelta] = None) -> List[Submission]:
        """Collect posts from the subreddit within an optional time limit using Reddit's new submissions.

        Args:
            limit (Optional[timedelta]): Optional time limit for post collection.

        Returns:
            List[Submission]: List of collected posts.

        Raises:
            Exception: If post collection fails.
        """
        posts = []
        now = datetime.now(timezone.utc)

        if limit:
            start_time = now - limit
            frog.info(f"Collecting posts between {start_time} and {now}")
        else:
            start_time = None
            frog.info("Collecting recent posts")

        try:
            for submission in self.subreddit.new(limit=None):
                submission_time = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc)
                if start_time and submission_time < start_time:
                    break
                posts.append(submission)
                if len(posts) % 100 == 0:
                    frog.debug(f"Collected {len(posts)} posts")

            frog.info(f"Successfully collected {len(posts)} posts")
            return posts

        except Exception as e:
            frog.error(f"Error collecting posts: {str(e)}")
            raise

    def _collect_time_stats(self, period: TimePeriod) -> None:
        """Collect time-based statistics for a specific period.

        Args:
            period (TimePeriod): Time period to collect statistics for.

        Raises:
            Exception: If statistics collection fails.
        """
        frog.info(f"Collecting stats for period: {period.value}")
        try:
            time_limit = period.to_timedelta()
            posts = self._collect_posts(time_limit)
            self.time_stats[period] = TimeStats.from_posts(posts, period)
            frog.info(
                f"Completed stats collection for {period.value}: "
                f"{len(posts)} posts processed"
            )

        except Exception as e:
            frog.error(f"Failed to collect stats for {period.value}: {str(e)}")
            raise

    def collect(self) -> "SubredditStats":
        """Collect all configured statistics.

        Returns:
            SubredditStats: Self reference for method chaining.

        Raises:
            Exception: If statistics collection fails.
        """
        frog.info(f"Starting stats collection for r/{self.subreddit_name}")

        try:
            # Collect basic metrics
            sub = self.subreddit
            self.metrics = SubredditMetrics(
                subscribers=sub.subscribers or 0,
                active_users=sub.active_user_count or 0,
                created_at=sub.created_utc,
            )
            frog.info(
                f"Collected basic metrics: {self.metrics.subscribers:,} subscribers, "
                f"{self.metrics.active_users:,} active users"
            )

            # Collect time stats if periods were specified
            if self.time_periods:
                for period in self.time_periods:
                    self._collect_time_stats(period)

            frog.info("Stats collection completed successfully")
            return self

        except Exception as e:
            frog.error(f"Stats collection failed: {str(e)}")
            raise

    def get_summary(self) -> str:
        """Generate a human-readable summary of the collected statistics.

        Returns:
            str: Formatted summary of statistics.
        """
        if not self.metrics:
            return "No stats collected yet"

        summary = [
            f"r/{self.subreddit_name} Statistics",
            f"Subscribers: {self.metrics.subscribers:,}",
            f"Active Users: {self.metrics.active_users:,}",
            f"Created: {self.metrics.created_at.strftime('%Y-%m-%d')}",
        ]

        # Sort periods by length (day, week, month, year, all)
        sorted_periods = sorted(
            self.time_stats.items(), key=lambda x: list(TimePeriod).index(x[0])
        )

        for period, stats in sorted_periods:
            summary.extend(
                [
                    f"\n{period.value.capitalize()} Stats:",
                    f"- Total Posts: {stats.total_posts:,}",
                    f"- Average Upvotes: {stats.avg_upvotes:.1f}",
                    f"- Median Upvotes: {stats.median_upvotes:,}",
                    f"- Posts per Day: {stats.posts_per_day:.1f}",
                ]
            )

        return "\n".join(summary)


if __name__ == "__main__":
    frog.setLevel("DEBUG")

    stats_workingout = None
    try:
        stats_workingout = SubredditStats("Workingout", time_periods=["day", "month", "year"])
        stats_workingout.collect()
    except Exception as e:
        print(f"Error running example for 'Workingout': {str(e)}")

    stats_woodcarving = None
    try:
        stats_woodcarving = SubredditStats("Woodcarving", time_periods=["day", "month", "year"])
        stats_woodcarving.collect()
    except Exception as e:
        print(f"Error running example for 'Woodcarving': {str(e)}")

    if stats_workingout:
        print(stats_workingout.get_summary())
    print('\n\n')
    if stats_woodcarving:
        print(stats_woodcarving.get_summary())
