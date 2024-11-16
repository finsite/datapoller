import yfinance as yf
from app.pollers.base_poller import BasePoller
import logging

# Configure logging
logger = logging.getLogger(__name__)

class YFinancePoller(BasePoller):
    def __init__(self, api_key=None):
        super().__init__(api_key)
        self.base_url = "https://query1.finance.yahoo.com/v7/finance/quote"

    def poll(self, symbols):
        results = {}
        for symbol in symbols:
            try:
                data = yf.Ticker(symbol)
                quote = data.history(period="1d")
                if quote.empty:
                    raise ValueError(f"No data returned for symbol: {symbol}")
                results[symbol] = quote.to_dict(orient="records")
            except ValueError as e:
                logger.error(f"ValueError for symbol {symbol}: {e}")
                results[symbol] = {"error": str(e)}
            except Exception as e:
                logger.error(f"Error fetching data for symbol {symbol}: {e}")
                results[symbol] = {"error": f"Unexpected error: {str(e)}"}

        self.send_to_queue(results)
        return results
