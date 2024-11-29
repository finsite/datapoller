from app.pollers.base_poller import BasePoller
from app.utils.retry_request import retry_request
from app.utils.validate_data import validate_data
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.request_with_timeout import request_with_timeout
from app.utils.validate_environment_variables import validate_environment_variables


class FinnhubPoller(BasePoller):
    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "FINNHUB_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: list):
        for symbol in symbols:
            try:

                def request_func():
                    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.api_key}"
                    return request_with_timeout("GET", url)

                data = retry_request(request_func)

                if not data or "c" not in data:
                    track_request_metrics("failure", source="Finnhub")
                    continue

                payload = {
                    "symbol": symbol,
                    "timestamp": None,  # Finnhub does not provide timestamps in quotes
                    "price": float(data["c"]),
                    "source": "Finnhub",
                    "data": {
                        "current": float(data["c"]),
                        "high": float(data["h"]),
                        "low": float(data["l"]),
                        "open": float(data["o"]),
                        "previous_close": float(data["pc"]),
                    },
                }

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="Finnhub")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="Finnhub")
