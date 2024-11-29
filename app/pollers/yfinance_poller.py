from app.pollers.base_poller import BasePoller
from app.utils.retry_request import retry_request
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables
import yfinance as yf


class YFinancePoller(BasePoller):
    def __init__(self):
        super().__init__()
        # Add required environment variables
        validate_environment_variables(["SQS_QUEUE_URL"])

    def poll(self, symbols: list):
        for symbol in symbols:
            try:

                def fetch_data_func():
                    """Function to fetch data, wrapped for retry handling."""
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    if hist.empty:
                        raise ValueError(f"No data found for symbol: {symbol}")
                    return hist.iloc[-1]

                latest_data = retry_request(fetch_data_func)

                # Construct payload
                payload = {
                    "symbol": symbol,
                    "timestamp": latest_data.name.isoformat(),
                    "price": float(latest_data["Close"]),
                    "source": "YFinance",
                    "data": {
                        "open": float(latest_data["Open"]),
                        "high": float(latest_data["High"]),
                        "low": float(latest_data["Low"]),
                        "close": float(latest_data["Close"]),
                        "volume": int(latest_data["Volume"]),
                    },
                }

                validate_data(payload)  # Validate the payload structure
                self.send_to_queue(payload)  # Send data to the queue
                track_polling_metrics("success")  # Track polling success
                # Track request success
                track_request_metrics("success", source="YFinance")
            except Exception as e:
                # Log and track failures
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="YFinance")
