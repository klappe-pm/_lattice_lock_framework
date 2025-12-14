
# IMPLEMENTATION PROTOTYPE (Agent C_7_3)
# Task 7.3: Advanced Telemetry

import time
import functools

class Telemetry:
    def __init__(self):
        self.metrics = {}

    def track_latency(self, name: str):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration = (time.perf_counter() - start) * 1000
                    print(f"[METRIC] {name}_latency_ms: {duration:.2f}")
            return wrapper
        return decorator

    def inc_counter(self, name: str, value: int = 1):
        print(f"[METRIC] {name}_count: +{value}")

if __name__ == "__main__":
    telemetry = Telemetry()

    @telemetry.track_latency("generation")
    def mock_gen():
        time.sleep(0.1)

    mock_gen()
    telemetry.inc_counter("errors", 1)
