from app.pollers.base_poller import BasePoller
from app.utils.retry_request import retry_request
from app.utils.validate_data import validate_data
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.request_with_timeout import request_with_timeout
from app.utils.validate_environment_variables import validate_environment_variables


class PolygonPoller(BasePoller):
    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "POLYGON_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: list):
        for symbol in symbols:
            try:

                def request_func():
                    url = f"https://api.polygon.io/v1/last/stocks/{symbol}?apiKey={self.api_key}"
                    return request_with_timeout("GET", url)

                data = retry_request(request_func)

                if "status" not in data or data["status"] != "success":
                    track_request_metrics("failure", source="Polygon")
                    continue

                payload = {
                    "symbol": data["symbol"],
                    "timestamp": data["last"]["timestamp"],
                    "price": float(data["last"]["price"]),
                    "source": "Polygon",
                    "data": {
                        "size": data["last"]["size"],
                        "exchange": data["last"]["exchange"],
                    },
                }

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="Polygon")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="Polygon")
