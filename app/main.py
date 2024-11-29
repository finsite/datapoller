import os
import time
import logging
from app.pollers import (
    FinnhubPoller,
    PolygonPoller,
    AlphaVantagePoller,
    YfinancePoller,
    IexPoller,
    QuandlPoller,
)
from app.utils import (
    validate_environment_variables,
    track_request_metrics,
    track_polling_metrics,
)
from app.queue import QueueSender


# Set up logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# Validate required environment variables
validate_environment_variables()

# Queue Configuration
QUEUE_TYPE = os.getenv("QUEUE_TYPE", "rabbitmq")
QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")

# Polling interval and retries
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))

# Initialize the queue sender based on the environment variable
queue_sender = QueueSender(queue_type=QUEUE_TYPE, queue_url=QUEUE_URL)

# Poller Types Configuration
POLLER_TYPE = os.getenv("POLLER_TYPE", "finnhub")

# API keys for various pollers
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
YFINANCE_API_KEY = os.getenv("YFINANCE_API_KEY")
IEX_API_KEY = os.getenv("IEX_API_KEY")
QUANDL_API_KEY = os.getenv("QUANDL_API_KEY")

# Create Poller based on the configured type
if POLLER_TYPE == "finnhub":
    poller = FinnhubPoller(FINNHUB_API_KEY)
elif POLLER_TYPE == "polygon":
    poller = PolygonPoller(POLYGON_API_KEY)
elif POLLER_TYPE == "alphavantage":
    poller = AlphaVantagePoller(ALPHA_VANTAGE_API_KEY)
elif POLLER_TYPE == "yfinance":
    poller = YfinancePoller(YFINANCE_API_KEY)
elif POLLER_TYPE == "iex":
    poller = IexPoller(IEX_API_KEY)
elif POLLER_TYPE == "quandl":
    poller = QuandlPoller(QUANDL_API_KEY)
else:
    logger.error(f"Unsupported poller type: {POLLER_TYPE}")
    raise ValueError(f"Unsupported poller type: {POLLER_TYPE}")


# Main polling loop
def main():
    try:
        logger.info(f"Starting {POLLER_TYPE} poller...")
        while True:
            symbols = get_symbols_to_poll()
            logger.info(f"Polling for symbols: {symbols}")

            # Track polling metrics before polling
            track_polling_metrics(POLLER_TYPE, symbols)

            # Poll and track request metrics for each symbol
            for symbol in symbols:
                logger.info(f"Polling data for {symbol}")
                track_request_metrics(symbol, REQUEST_TIMEOUT, MAX_RETRIES)

                poller.poll(
                    [symbol]
                )  # Assuming poller handles a single symbol in this iteration

                # Optionally, send to queue after polling
                queue_sender.send(symbol)

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Polling stopped by user.")
    except Exception as e:
        logger.error(f"An error occurred during polling: {e}")
    finally:
        logger.info("Shutting down...")
        queue_sender.close()


def get_symbols_to_poll():
    """
    Get the list of stock symbols to poll. This can be customized as needed.
    """
    return os.getenv("SYMBOLS", "AAPL,GOOG,MSFT").split(",")


if __name__ == "__main__":
    main()
