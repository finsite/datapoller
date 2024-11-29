import os

from app.pollers.alphavantage_poller import AlphaVantagePoller
from app.pollers.finnhub_poller import FinnhubPoller
from app.pollers.iex_poller import IEXPoller
from app.pollers.polygon_poller import PolygonPoller
from app.pollers.quandl_poller import QuandlPoller
from app.pollers.yfinance_poller import YFinancePoller
from app.utils.setup_logger import setup_logger
from app.utils.validate_environment_variables import validate_environment_variables

# Initialize logger
logger = setup_logger()


class PollerFactory:
    def __init__(self):
        """
        Initializes the PollerFactory, validating the required environment variables and
        determining the appropriate poller class based on the configuration.
        """
        # Validate required environment variables
        required_env_vars = [
            "POLLER_TYPE",
            "IEX_API_KEY",
            "FINNHUB_API_KEY",
            "POLYGON_API_KEY",
            "ALPHA_VANTAGE_API_KEY",
            "YFINANCE_API_KEY",
            "QUANDL_API_KEY",
        ]
        validate_environment_variables(required_env_vars)

        # Fetch poller configuration from environment variables
        self.poller_type = os.getenv("POLLER_TYPE").lower()

        if self.poller_type not in {
            "iex",
            "finnhub",
            "polygon",
            "alpha_vantage",
            "yfinance",
            "quandl",
        }:
            raise ValueError(
                "POLLER_TYPE must be one of: 'iex', 'finnhub', 'polygon', "
                "'alpha_vantage', 'yfinance', or 'quandl'."
            )

    def create_poller(self):
        """
        Creates an instance of the poller based on the specified POLLER_TYPE.

        Returns:
            poller: The appropriate poller instance (e.g., IEXPoller, FinnhubPoller).
        """
        # Create and return the poller instance based on the POLLER_TYPE
        if self.poller_type == "iex":
            api_key = os.getenv("IEX_API_KEY")
            logger.info("Using IEX Poller.")
            return IEXPoller(api_key)
        elif self.poller_type == "finnhub":
            api_key = os.getenv("FINNHUB_API_KEY")
            logger.info("Using Finnhub Poller.")
            return FinnhubPoller(api_key)
        elif self.poller_type == "polygon":
            api_key = os.getenv("POLYGON_API_KEY")
            logger.info("Using Polygon Poller.")
            return PolygonPoller(api_key)
        elif self.poller_type == "alpha_vantage":
            api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
            logger.info("Using Alpha Vantage Poller.")
            return AlphaVantagePoller(api_key)
        elif self.poller_type == "yfinance":
            api_key = os.getenv("YFINANCE_API_KEY")
            logger.info("Using YFinance Poller.")
            return YFinancePoller(api_key)
        elif self.poller_type == "quandl":
            api_key = os.getenv("QUANDL_API_KEY")
            logger.info("Using Quandl Poller.")
            return QuandlPoller(api_key)
        else:
            logger.error(f"Invalid POLLER_TYPE: {self.poller_type}")
            raise ValueError(f"Invalid POLLER_TYPE: {self.poller_type}")
