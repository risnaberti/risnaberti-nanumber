# nanumber/storage/memory.py
from threading import Lock
from .base import BaseStorage

class MemoryStorage(BaseStorage):
    def __init__(self):
        self._store = {}
        self._lock = Lock()

    def get_last_number(self, key: str) -> int:
        return self._store.get(key, 0)

    def increment(self, key: str) -> int:
        with self._lock:
            current = self._store.get(key, 0)
            next_val = current + 1
            self._store[key] = next_val
            return next_val

    def reset(self, key: str, value: int = 0):
        with self._lock:
            self._store[key] = value
