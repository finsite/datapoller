from pollers import YFinancePoller, PolygonPoller, IexPoller, AlphaVantagePoller, QuandlPoller
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

def create_poller():
    """
    Factory function to create and return the appropriate poller based on an environment variable.
    """
    poller_type = os.getenv("POLLING_PROVIDER", "yfinance").lower()

    if poller_type == "yfinance":
        logger.info("Creating YFinancePoller")
        return YFinancePoller()
    elif poller_type == "polygon":
        api_key = os.getenv("POLYGON_API_KEY")
        logger.info("Creating PolygonPoller")
        return PolygonPoller(api_key)
    elif poller_type == "iex":
        api_key = os.getenv("IEX_API_KEY")
        logger.info("Creating IEX Poller")
        return IexPoller(api_key)
    elif poller_type == "alphavantage":
        api_key = os.getenv("ALPHAVANTAGE_API_KEY")
        logger.info("Creating AlphaVantagePoller")
        return AlphaVantagePoller(api_key)
    elif poller_type == "quandl":
        api_key = os.getenv("QUANDL_API_KEY")
        logger.info("Creating QuandlPoller")
        return QuandlPoller(api_key)
    else:
        logger.error(f"Unsupported polling provider: {poller_type}")
        raise ValueError(f"Unsupported polling provider: {poller_type}")
