from dataclasses import dataclass, field
from typing import Dict, List
import time

@dataclass
class MetricsSnapshot:
    total_validations: int
    success_rate: float
    avg_response_time: float
    error_counts: Dict[str, int]
    health_score: int
    timestamp: float

class MetricsCollector:
    def __init__(self):
        self.validation_count = 0
        self.success_count = 0
        self.error_counts: Dict[str, int] = {}
        self.response_times: List[float] = []
        self._start_time = time.time()

    def record_validation(self, success: bool, duration: float, error_type: str = None):
        self.validation_count += 1
        if success:
            self.success_count += 1
        
        if error_type:
            self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
            
        self.response_times.append(duration)
        # Keep only last 1000 response times to avoid memory growth
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]

    def get_snapshot(self) -> MetricsSnapshot:
        success_rate = (self.success_count / self.validation_count * 100) if self.validation_count > 0 else 100.0
        avg_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        
        # Calculate health score (0-100)
        # Base 100, deduct for failures and high latency
        health = 100
        if self.validation_count > 0:
            failure_rate = 100 - success_rate
            health -= failure_rate * 2  # Heavy penalty for failures
            
            if avg_time > 1.0: # Penalty for >1s latency
                health -= (avg_time - 1.0) * 10
        
        return MetricsSnapshot(
            total_validations=self.validation_count,
            success_rate=round(success_rate, 2),
            avg_response_time=round(avg_time, 4),
            error_counts=self.error_counts.copy(),
            health_score=max(0, min(100, int(health))),
            timestamp=time.time()
        )
