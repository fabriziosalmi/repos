"""Disk-backed cache for GitHub API results."""

import datetime
import json
import logging
import os

CACHE_FILE = "github_stats_cache.json"
CACHE_DURATION_HOURS = 1


def load_cache():
    """Load cached data if it exists and is still valid."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            cache_time = datetime.datetime.fromisoformat(cache_data.get('timestamp', ''))
            now = datetime.datetime.now(datetime.timezone.utc)

            if (now - cache_time).total_seconds() < CACHE_DURATION_HOURS * 3600:
                logging.info("Using cached data (still valid)")
                return cache_data.get('data')

        logging.info("Cache not found or expired")
        return None
    except Exception as e:
        logging.warning(f"Error loading cache: {e}")
        return None


def save_cache(data):
    """Save data to cache."""
    try:
        cache_data = {
            'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'data': data
        }
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, default=str)
        logging.info("Data cached successfully")
    except Exception as e:
        logging.warning(f"Error saving cache: {e}")
