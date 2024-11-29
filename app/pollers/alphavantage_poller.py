import time
from app.pollers.base_poller import BasePoller
from app.utils.rate_limit import rate_limit
from app.utils.retry_request import retry_request
from app.utils.validate_data import validate_data
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.request_with_timeout import request_with_timeout
from app.utils.validate_environment_variables import validate_environment_variables


class AlphaVantagePoller(BasePoller):
    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "ALPHAVANTAGE_API_KEY"])
        self.api_key = api_key
        self.last_request_time = 0
        self.rate_limit_interval = 60  # 5 requests per minute

    def poll(self, symbols: list):
        for symbol in symbols:
            try:
                rate_limit(self.last_request_time, self.rate_limit_interval)
                self.last_request_time = time.time()

                def request_func():
                    url = (
                        f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
                        f"&symbol={symbol}&interval=5min&apikey={self.api_key}"
                    )
                    return request_with_timeout("GET", url)

                data = retry_request(request_func)

                if "Error Message" in data:
                    track_request_metrics("failure", source="AlphaVantage")
                    continue

                time_series = data["Time Series (5min)"]
                latest_time = max(time_series.keys())
                latest_data = time_series[latest_time]

                payload = {
                    "symbol": symbol,
                    "timestamp": latest_time,
                    "price": float(latest_data["4. close"]),
                    "source": "AlphaVantage",
                    "data": {
                        "open": float(latest_data["1. open"]),
                        "high": float(latest_data["2. high"]),
                        "low": float(latest_data["3. low"]),
                        "close": float(latest_data["4. close"]),
                        "volume": int(latest_data["5. volume"]),
                    },
                }

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="AlphaVantage")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="AlphaVantage")
