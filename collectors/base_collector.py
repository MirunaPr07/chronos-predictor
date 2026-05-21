import threading
import time
from abc import ABC, abstractmethod
from collectors.data_queue import DataQueue


class BaseCollector(ABC):
    """
    Abstract base class for all collectors.
    Each thread inherits from this class and implements collect().
    """

    def __init__(self, name: str, interval: int = 30):
        self.name = name
        self.interval = interval  # seconds between collections
        self.queue = DataQueue()
        self.is_running = False
        self._thread = None

    def start(self):
        """Start the collection thread."""
        self.is_running = True
        self._thread = threading.Thread(
            target=self._run,
            name=f"Thread-{self.name}",
            daemon=True  # auto stops when the program exits
        )
        self._thread.start()
        print(f"[{self.name}] Thread started")

    def stop(self):
        """Stop the collection thread."""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        print(f"[{self.name}] Thread stopped")

    def _run(self):
        """Main loop for the thread."""
        while self.is_running:
            try:
                data = self.collect()
                if data:
                    self.queue.put(data)
                    print(f"[{self.name}] Collected data: {data}")
            except Exception as e:
                print(f"[{self.name}] Error: {e}")
            time.sleep(self.interval)

    @abstractmethod
    def collect(self) -> dict:
        """
        Each collector implements this method.
        It must return a dict with the collected data.
        """
        pass