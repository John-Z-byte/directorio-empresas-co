import logging
import time
from dataclasses import dataclass

def setup_logger(name: str = "directorio") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    h = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    h.setFormatter(fmt)
    logger.addHandler(h)
    return logger

@dataclass(frozen=True)
class StepTimer:
    step: str
    t0: float

    @staticmethod
    def start(step: str) -> "StepTimer":
        return StepTimer(step=step, t0=time.perf_counter())

    def done(self) -> float:
        return time.perf_counter() - self.t0
    
from pathlib import Path

def file_mb(path: str | Path) -> float:
    p = Path(path)
    if not p.exists():
        return 0.0
    return round(p.stat().st_size / (1024 * 1024), 2)
