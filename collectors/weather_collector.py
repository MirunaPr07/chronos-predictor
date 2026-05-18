import requests
from datetime import datetime
from django.conf import settings
from collectors.base_collector import BaseCollector


class WeatherCollector(BaseCollector):
    """
    Thread 1 — Colecteaza date meteo de la OpenWeatherMap API.
    """

    def __init__(self):
        super().__init__(name="WeatherCollector", interval=60)
        self.api_key = settings.OPENWEATHER_API_KEY
        self.city = "Bucharest"
        self.url = f"http://api.openweathermap.org/data/2.5/weather"

    def collect(self) -> dict:
        if not self.api_key:
            # Daca nu avem API key, generam date simulate
            return self._simulate()

        response = requests.get(self.url, params={
            "q": self.city,
            "appid": self.api_key,
            "units": "metric"
        })
        response.raise_for_status()
        data = response.json()

        return {
            "source": "weather",
            "timestamp": datetime.utcnow().isoformat(),
            "value": data["main"]["temp"],
            "unit": "celsius",
            "extra": {
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
            }
        }

    def _simulate(self) -> dict:
        """Date simulate cand nu avem API key"""
        import random
        return {
            "source": "weather",
            "timestamp": datetime.utcnow().isoformat(),
            "value": round(random.uniform(15.0, 35.0), 2),
            "unit": "celsius",
            "extra": {
                "humidity": random.randint(40, 90),
                "pressure": random.randint(1000, 1025),
                "description": "simulated",
            }
        }