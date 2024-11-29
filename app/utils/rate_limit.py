import time

from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)


class RateLimiter:
    """A rate limiter that enforces a certain number of calls within a time period."""

    def __init__(self, poll_interval: int):
        """Initialize the rate limiter.

        Args:
            poll_interval (int): The time period in seconds between each poll.
        """
        self.poll_interval = poll_interval
        self._last_request_time = 0

    def wait(self):
        """Wait if the rate limit has been reached."""
        current_time = time.time()
        time_to_wait = self.poll_interval - (current_time - self._last_request_time)
        if time_to_wait > 0:
            logger.info(f"Rate limit reached. Sleeping for {time_to_wait:.2f} seconds.")
            time.sleep(time_to_wait)
        self._last_request_time = current_time
