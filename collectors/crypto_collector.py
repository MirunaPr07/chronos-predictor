import requests
from datetime import datetime
from collectors.base_collector import BaseCollector


class CryptoCollector(BaseCollector):
    # thread 2: we collect prices from CoinGecko API
    # no need for API key

    def __init__(self):
        super().__init__(name="CryptoCollector", interval=30)
        self.url = "https://api.coingecko.com/api/v3/simple/price"
        self.coin = "bitcoin"

    def collect(self) -> dict:
        try:
            response = requests.get(self.url, params={
                "ids": self.coin,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_last_updated_at": "true",
            }, timeout=10)
            response.raise_for_status()
            data = response.json()[self.coin]

            return {
                "source": "crypto",
                "timestamp": datetime.utcnow().isoformat(),
                "value": data["usd"],
                "unit": "usd",
                "extra": {
                    "coin": self.coin,
                    "change_24h": data.get("usd_24h_change", 0),
                    "last_updated": data.get("last_updated_at", 0),
                }
            }
        except Exception:
            return self._simulate()

    def _simulate(self) -> dict:
        # simulated data when API is not available
        import random
        return {
            "source": "crypto",
            "timestamp": datetime.utcnow().isoformat(),
            "value": round(random.uniform(25000, 70000), 2),
            "unit": "usd",
            "extra": {
                "coin": self.coin,
                "change_24h": round(random.uniform(-5.0, 5.0), 2),
                "last_updated": 0,
            }
        }