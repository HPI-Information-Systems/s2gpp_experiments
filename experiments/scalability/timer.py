import time
from typing import Optional


class Timer:
    def __init__(self):
        self.start_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
