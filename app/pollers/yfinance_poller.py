import yfinance as yf
from app.pollers.base_poller import BasePoller
from app.utils.validate_data import validate_data
from app.utils.track_polling_metrics import track_polling_metrics
from app.utils.track_request_metrics import track_request_metrics
from app.utils.validate_environment_variables import validate_environment_variables


class YFinancePoller(BasePoller):
    def __init__(self):
        super().__init__()
        validate_environment_variables(["SQS_QUEUE_URL"])

    def poll(self, symbols: list):
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                history = stock.history(period="1d", interval="1m")

                if history.empty:
                    track_request_metrics("failure", source="YFinance")
                    continue

                latest_data = history.iloc[-1]

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

                validate_data(payload)
                self.send_to_queue(payload)
                track_polling_metrics("success")
                track_request_metrics("success", source="YFinance")
            except Exception as e:
                track_polling_metrics("failure", error=str(e))
                track_request_metrics("failure", source="YFinance")
