# nanumber/storage/base.py
from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    def get_last_number(self, key: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def increment(self, key: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def reset(self, key: str, value: int = 0):
        raise NotImplementedError
