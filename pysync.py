# pysync.py
import threading
from typing import Generic, TypeVar

T = TypeVar('T')

class GenProdCons(Generic[T]):
    def __init__(self, size: int = 10):
        if size <= 0:
            raise ValueError("Buffer size must be greater than 0")
        self.size = size
        self.buffer = []
        self.condition = threading.Condition()

    def put(self, e: T):
        with self.condition:
            while len(self.buffer) >= self.size:
                self.condition.wait()
            self.buffer.append(e)
            self.condition.notify_all()

    def get(self) -> T:
        with self.condition:
            while not self.buffer:
                self.condition.wait()
            e = self.buffer.pop(0)
            self.condition.notify_all()
            return e

    def __len__(self):
        with self.condition:
            return len(self.buffer)

class RendezvousDEchange(Generic[T]):
    def __init__(self):
        self.condition = threading.Condition()
        self.first_value = None
        self.exchange_ready = False

    def echanger(self, value: T) -> T:
        with self.condition:
            if not self.exchange_ready:
                self.first_value = value
                self.exchange_ready = True
                self.condition.wait()
                other = self.first_value
                self.first_value = None
                self.exchange_ready = False
                self.condition.notify()
                return other
            else:
                other = self.first_value
                self.first_value = value
                self.condition.notify()
                self.condition.wait()
                return other
