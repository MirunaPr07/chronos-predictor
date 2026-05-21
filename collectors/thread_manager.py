import threading
from collectors.weather_collector import WeatherCollector
from collectors.crypto_collector import CryptoCollector
from collectors.sensor_collector import SensorCollector
from collectors.historical_collector import HistoricalCollector
from collectors.data_queue import DataQueue

class ThreadManager:
	# in this class, we manage all collector threads (worker threads)
    def __init__(self):
        # initializing all 4 collectors:
        self.collectors = [
            WeatherCollector(),
            CryptoCollector(),
            SensorCollector(),
            HistoricalCollector(),
        ]
        self.queue = DataQueue()
        self._processor_thread = None
        self._is_processing = False

    def start_all(self):
        # starting all threads at the same time
        print("[ThreadManager] Starting all collector threads...")
        for collector in self.collectors:
            collector.start()
        # start the processor thread that reads from the queue
        self._is_processing = True
        self._processor_thread = threading.Thread(
            target=self._process_queue,
            name="Thread-Processor",
            daemon=True
        )
        self._processor_thread.start()
        print(f"[ThreadManager] All {len(self.collectors)} threads running!")

    def stop_all(self):
        print("[ThreadManager] Stopping all threads...")
        for collector in self.collectors:
            collector.stop()
        self._is_processing = False
        print("[ThreadManager] All threads stopped")

    def _process_queue(self):
        # in this function, we read data from the queue and save it into the database
        # imports here, to avoid circular imports with django:
        import django
        import os
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        django.setup()

        from api.models import RawData, DataSource
        from django.utils import timezone
        from datetime import datetime

        while self._is_processing:
            try:
                data = self.queue.get()
                self._save_to_db(data, RawData, DataSource)
            except Exception as e:
                print(f"[ThreadManager] Error processing queue item: {e}")

    def _save_to_db(self, data: dict, RawData, DataSource):
        # get or create the data source entry
        source, _ = DataSource.objects.get_or_create(
            name=data["source"],
            defaults={"url": "", "is_active": True}
        )
        # we save the raw data point:
        RawData.objects.create(
            source=source,
            timestamp=data["timestamp"],
            value=data["value"],
            unit=data.get("unit", ""),
            extra=data.get("extra", {}),
        )
        print(f"[ThreadManager] Saved to DB: {data['source']} | {data['value']}")

    def status(self) -> dict:
        # the current status of the threads: useful for the API
        return {
            "threads": [
                {
                    "name": c.name,
                    "is_running": c.is_running,
                    "interval": c.interval,
                }
                for c in self.collectors
            ],
            "queue_size": self.queue.size(),
        }