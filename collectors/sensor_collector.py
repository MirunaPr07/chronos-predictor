import random
import math
from datetime import datetime
from collectors.base_collector import BaseCollector


class SensorCollector(BaseCollector):
    # the third thread:
    # simulating data from sensors
	# generating realist data with noise and sin patterns

    def __init__(self):
        super().__init__(name="SensorCollector", interval=10)
        self._tick = 0  # contor pentru pattern sinusoidal

    def collect(self) -> dict:
        self._tick += 1
        # we simulate sin pattern and random noise, so we work with realist data:
        base_value = 50.0
        wave = math.sin(self._tick * 0.1) * 20
        noise = random.uniform(-2.0, 2.0)
        spike = self._generate_spike()

        value = round(base_value + wave + noise + spike, 2)
        return {
            "source": "sensor",
            "timestamp": datetime.utcnow().isoformat(),
            "value": value,
            "unit": "kwh",
            "extra": {
                "sensor_id": "SENSOR_001",
                "location": "Factory Floor A",
                "tick": self._tick,
                "is_spike": spike != 0,
            }
        }

    def _generate_spike(self) -> float:
        # we generate an occasional spike for testing alerts
        if random.random() < 0.05:
            return random.uniform(20.0, 40.0)
        return 0.0