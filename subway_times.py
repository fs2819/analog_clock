"""Subway time service with caching.

Translated from SubwayTimeService/handler/main.go (HandleRequest + prepareResponse).
Instead of DynamoDB, we cache in memory since this runs locally on the Pi.
"""

import logging
import time

from config import CACHE_TTL_SECONDS, NUM_HANDS
from mta_feed import StationTimes, get_next_arrivals

logger = logging.getLogger(__name__)

_cached_times: StationTimes | None = None


def get_minutes_to_next_trains() -> list[float]:
    """Return sorted list of minutes until upcoming 1-train arrivals.

    Uses a simple in-memory cache (replaces DynamoDB from the Go version).
    """
    global _cached_times

    now = time.time()
    cache_expired = (
        _cached_times is None
        or (now - _cached_times.fetch_timestamp) > CACHE_TTL_SECONDS
    )

    if cache_expired:
        logger.info("Cache expired, refreshing from MTA feed")
        try:
            _cached_times = get_next_arrivals()
        except Exception:
            logger.exception("Failed to fetch MTA data")
            if _cached_times is not None:
                logger.warning("Using stale cached data")
            else:
                return []

    # Recalculate minutes from current time (arrivals store absolute unix times)
    minutes = []
    for arrival in _cached_times.arrivals:
        mins = (arrival.unix_time - time.time()) / 60.0
        if mins > 0:
            minutes.append(round(mins, 1))

    minutes.sort()
    return minutes[:NUM_HANDS]


def get_next_train_minutes() -> list[float | None]:
    """Return minutes for the closest NUM_HANDS trains.

    Always returns a list of length NUM_HANDS. Positions without a known
    train are filled with None.
    """
    upcoming = get_minutes_to_next_trains()
    result: list[float | None] = list(upcoming[:NUM_HANDS])
    while len(result) < NUM_HANDS:
        result.append(None)
    return result
