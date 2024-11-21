import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.calls = 0
        self.start_time = time.time()
        self.max_calls = max_calls
        self.period = period
    
    def allow(self):
        if time.time() - self.start_time > self.period:
            self.start_time = time.time()
            self.calls = 0
        self.calls += 1
        return self.calls <= self.max_calls
