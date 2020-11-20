"""This module provides functionality for database interactions."""

from gino.ext.aiohttp import Gino

from app import config


db = Gino()


def get_database_dsn():
    """Return database dsn based on server mode."""
    return getattr(config, f"POSTGRES_DSN_{config.SERVER_MODE}")
