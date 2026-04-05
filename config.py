"""Configuration for the analog clock subway time service."""

# MTA GTFS-Realtime feed URL for 1/2/3/4/5/6/7 trains
FEED_URL = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs"

# Station: 125th St on the 1 train, southbound (downtown)
STATION_ID = "116S"
STATION_NAME = "125th St"
ROUTE_ID = "1"

# How often to poll the MTA feed (seconds)
POLL_INTERVAL_SECONDS = 15

# Cache duration — don't re-fetch if data is newer than this (seconds)
CACHE_TTL_SECONDS = 60

# Number of clock hands (show the N soonest trains)
NUM_HANDS = 3

# Logging
LOG_LEVEL = "INFO"
