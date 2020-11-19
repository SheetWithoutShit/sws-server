"""This module provides functionality for database interactions."""

from app import config
from gino.ext.aiohttp import Gino


db = Gino()


def get_database_dsn():
    """Return database dsn based on server mode."""
    return getattr(config, f"POSTGRES_DSN_{config.SERVER_MODE}")
