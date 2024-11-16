import requests
from app.pollers.base_poller import BasePoller
import logging

# Configure logging
logger = logging.getLogger(__name__)

class AlphaVantagePoller(BasePoller):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.base_url = "https://www.alphavantage.co/query"

    def poll(self, symbols):
        results = {}
        for symbol in symbols:
            try:
                url = f"{self.base_url}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.api_key}"
                response = requests.get(url)

                if response.status_code == 200:
                    results[symbol] = response.json().get('Time Series (Daily)', {})
                else:
                    raise ValueError(f"API request failed for {symbol}, status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                logger.error(f"RequestException for symbol {symbol}: {e}")
                results[symbol] = {"error": f"RequestException: {str(e)}"}
            except ValueError as e:
                logger.error(f"ValueError for symbol {symbol}: {e}")
                results[symbol] = {"error": f"ValueError: {str(e)}"}
            except Exception as e:
                logger.error(f"Unexpected error for symbol {symbol}: {e}")
                results[symbol] = {"error": f"Unexpected error: {str(e)}"}

        self.send_to_queue(results)
        return results
