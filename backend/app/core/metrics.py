# app/core/metrics.py
import os
import time
from typing import Any

from app.core.logger import get_logger
from app.core.config import METRICS_ENABLED

logger = get_logger("metrics")


def now() -> float:
    """Monotonic start time for duration measurement."""
    return time.perf_counter()


def _fmt(fields: dict[str, Any]) -> str:
    parts: list[str] = []
    for k, v in fields.items():
        if v is None:
            continue
        parts.append(f"{k}={v}")
    return "|".join(parts)


def span(name: str, start: float, **fields: Any) -> int:
    """Emit a span metric log and return elapsed ms."""
    if not METRICS_ENABLED:
        return -1
    ms = int((time.perf_counter() - start) * 1000)
    base = f"METRIC|event=span|name={name}|ms={ms}"
    extra = _fmt(fields)
    logger.info(base + (f"|{extra}" if extra else ""))
    return ms


def mark(name: str, **fields: Any) -> None:
    """Emit a mark log (no duration)."""
    if not METRICS_ENABLED:
        return
    base = f"METRIC|event=mark|name={name}"
    extra = _fmt(fields)
    logger.info(base + (f"|{extra}" if extra else ""))