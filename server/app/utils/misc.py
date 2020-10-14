"""This module provides misc functions."""

import asyncio
import logging

from app.utils.errors import RetryError


LOGGER = logging.getLogger(__name__)


def retry(times, retry_interval=2):
    """Decorator that provides backoff retries."""
    def func_wrapper(func):
        """Function wrapper."""
        async def wrapper(*args, **kwargs):
            """The main functionality of backoff retries leaves here."""
            for time in range(times):
                try:
                    return await func(*args, **kwargs)
                except RetryError:
                    await asyncio.sleep(retry_interval ** time)
                    LOGGER.error(
                        "%s(args: %s, kwargs: %s) ... Retrying, attempt #%s.",
                        func.__name__,
                        args,
                        kwargs,
                        time + 1
                    )

        return wrapper
    return func_wrapper
