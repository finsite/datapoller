import os
import time
from app.poller_factory import PollerFactory
from app.utils.rate_limit import RateLimiter
from app.utils.setup_logger import setup_logger
from app.utils import (
    validate_environment_variables,
    track_request_metrics,
    track_polling_metrics,
)
from app.queue.queue_sender import QueueSender

# Set up logging
logger = setup_logger(__name__)

# Validate required environment variables
required_env_vars = [
    "POLLER_TYPE",
    "QUEUE_TYPE",
    "SYMBOLS",
]
validate_environment_variables(required_env_vars)

# Queue Configuration
QUEUE_TYPE = os.getenv("QUEUE_TYPE", "rabbitmq")
QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")

if QUEUE_TYPE not in ["rabbitmq", "sqs"]:
    raise ValueError(f"Unsupported QUEUE_TYPE: {QUEUE_TYPE}")

# Polling interval and retries
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))

# Initialize RateLimiter
RATE_LIMIT = int(os.getenv("RATE_LIMIT", 5))  # Requests per second
rate_limiter = RateLimiter(max_requests=RATE_LIMIT, time_window=1)

# Initialize the queue sender
queue_sender = QueueSender(queue_type=QUEUE_TYPE, queue_url=QUEUE_URL)

# Initialize the PollerFactory and create the poller
poller_factory = PollerFactory()
poller = poller_factory.create_poller()


def main():
    """
    Main polling loop.
    Polls data for configured symbols and sends the results to a queue.
    """
    try:
        logger.info(f"Starting {poller_factory.poller_type.capitalize()} Poller...")
        logger.info(
            f"Polling with QUEUE_TYPE={QUEUE_TYPE}, POLL_INTERVAL={POLL_INTERVAL}s"
        )
        while True:
            symbols = get_symbols_to_poll()
            logger.info(f"Polling for symbols: {symbols}")

            # Track polling metrics
            track_polling_metrics(poller_factory.poller_type, symbols)

            # Poll and send data for each symbol
            for symbol in symbols:
                rate_limiter.acquire(context=f"{poller_factory.poller_type} - {symbol}")
                try:
                    logger.info(f"Polling data for {symbol}")
                    track_request_metrics(symbol, REQUEST_TIMEOUT, MAX_RETRIES)
                    data = poller.poll([symbol])  # Assuming poller handles a single symbol
                    queue_sender.send(data)
                except Exception as e:
                    logger.error(f"Error polling {symbol}: {e}")

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Shutting down...")
        queue_sender.close()


def get_symbols_to_poll():
    """
    Get the list of stock symbols to poll.

    Defaults to 'AAPL,GOOG,MSFT' if SYMBOLS is not set in the environment.
    """
    return os.getenv("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


if __name__ == "__main__":
    main()
