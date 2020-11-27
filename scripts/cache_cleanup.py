import logging
import asyncio
import argparse

from app.cache import cache

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
LOGGER.addHandler(ch)


async def clean_cache(keys):
    """Delete cache item from Redis by key."""
    LOGGER.debug("Started script for cache cleaning...")
    for key in keys:
        await cache.set("test", "test")
        status = await cache.delete(key)
        LOGGER.debug("Deleting key=<%s> from cache. Status: %s.", key, bool(status))

    LOGGER.debug("Finished script for cache cleaning.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Clean up cache by keys.")
    parser.add_argument("keys", help="keys for cleaning", nargs="+")

    args = parser.parse_args()

    asyncio.run(clean_cache(args.keys))

