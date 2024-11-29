from app.pollers.base_poller import BasePoller
from app.utils.retry_request import retry_request
from app.utils.validate_data import validate_data
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.request_with_timeout import request_with_timeout
from app.utils.validate_environment_variables import validate_environment_variables


class IEXPoller(BasePoller):
    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "IEX_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: list):
        for symbol in symbols:
            try:

                def request_func():
                    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={self.api_key}"
                    return request_with_timeout("GET", url)

                data = retry_request(request_func)

                if not data:
                    track_request_metrics("failure", source="IEX")
                    continue

                payload = {
                    "symbol": data["symbol"],
                    "timestamp": data["latestUpdate"],
                    "price": float(data["latestPrice"]),
                    "source": "IEX",
                    "data": {
                        "open": float(data["open"]),
                        "high": float(data["high"]),
                        "low": float(data["low"]),
                        "close": float(data["latestPrice"]),
                        "volume": int(data["volume"]),
                    },
                }

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="IEX")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="IEX")
