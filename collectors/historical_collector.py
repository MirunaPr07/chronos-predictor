import csv
import os
import random
from datetime import datetime, timedelta
from collectors.base_collector import BaseCollector


class HistoricalCollector(BaseCollector):
	# thread 4 reads historical data from a CSV file
    # basically replays old data so the LSTM has something to train on
    def __init__(self):
        super().__init__(name="HistoricalCollector", interval=15)
        self.csv_path = os.path.join("data", "historical_data.csv")
        self._index = 0
        self._data = []
        self._load_csv()

    def _load_csv(self):
        # we try to load the CSV file, generate new data if it doesn't exist
        if os.path.exists(self.csv_path):
            with open(self.csv_path, "r") as f:
                reader = csv.DictReader(f)
                self._data = list(reader)
            print(f"[HistoricalCollector] Loaded {len(self._data)} rows from CSV")
        else:
            # no CSV yet, just generate fake historical data
            print("[HistoricalCollector] No CSV found, generating fake historical data")
            self._data = self._generate_fake_history()

    def collect(self) -> dict:
        if not self._data:
            return None
        # loop back to the start when we reach the end
        row = self._data[self._index % len(self._data)]
        self._index += 1
        return {
            "source": "historical",
            "timestamp": datetime.utcnow().isoformat(),
            "value": float(row.get("value", 0)),
            "unit": row.get("unit", "unknown"),
            "extra": {
                "original_timestamp": row.get("timestamp", ""),
                "row_index": self._index,
            }
        }

    def _generate_fake_history(self) -> list:
        # we generate 200 fake data points going back in time
        # it works for testing
        fake_data = []
        base_time = datetime.utcnow() - timedelta(hours=200)
        for i in range(200):
            fake_data.append({
                "timestamp": (base_time + timedelta(hours=i)).isoformat(),
                "value": round(random.uniform(20.0, 80.0), 2),
                "unit": "kwh",
            })
        return fake_data