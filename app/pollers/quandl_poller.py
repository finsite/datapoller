from app.pollers.base_poller import BasePoller
from app.utils.request_with_timeout import request_with_timeout
from app.utils.retry_request import retry_request
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_data import validate_data
from app.utils.validate_environment_variables import validate_environment_variables


class QuandlPoller(BasePoller):
    def __init__(self, api_key: str):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL", "QUANDL_API_KEY"])
        self.api_key = api_key

    def poll(self, symbols: list):
        for symbol in symbols:
            try:

                def request_func():
                    url = f"https://www.quandl.com/api/v3/datasets/WIKI/{symbol}.json?api_key={self.api_key}"
                    return request_with_timeout("GET", url)

                data = retry_request(request_func)

                if "dataset" not in data:
                    track_request_metrics("failure", source="Quandl")
                    continue

                dataset = data["dataset"]
                latest_data = dataset["data"][0]

                payload = {
                    "symbol": dataset["dataset_code"],
                    "timestamp": latest_data[0],
                    "price": float(latest_data[4]),
                    "source": "Quandl",
                    "data": {
                        "open": float(latest_data[1]),
                        "high": float(latest_data[2]),
                        "low": float(latest_data[3]),
                        "close": float(latest_data[4]),
                        "volume": int(latest_data[5]),
                    },
                }

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="Quandl")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="Quandl")
