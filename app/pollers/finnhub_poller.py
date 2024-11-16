from app.pollers.base_poller import BasePoller
import requests

class FinnhubPoller(BasePoller):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.base_url = "https://finnhub.io/api/v1/quote"

    def poll(self, symbols):
        results = {}
        for symbol in symbols:
            url = f"{self.base_url}/{symbol}"
            params = {"token": self.api_key}
            response = requests.get(url, params=params)
            results[symbol] = response.json()

        # Send the results to the queue
        self.send_to_queue(results)
        return results
