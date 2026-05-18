import queue
import threading


class DataQueue:
    """
    Coada shared intre thread-urile de colectare.
    Thread-urile pun date in coada, procesorul le scoate.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton — o singura coada pentru tot proiectul"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.queue = queue.Queue(maxsize=1000)
        return cls._instance

    def put(self, data: dict):
        """Adauga date in coada"""
        try:
            self.queue.put_nowait(data)
        except queue.Full:
            print("[DataQueue] Coada e plina, date aruncate!")

    def get(self):
        """Scoate date din coada (asteapta daca e goala)"""
        return self.queue.get(timeout=5)

    def size(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()