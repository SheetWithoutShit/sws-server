"""This module provides base class for instance to work with database."""


class DB:
    """Base class for interaction with database clients."""

    def __init__(self, postgres=None, redis=None):
        """Initialize instance with required database clients."""
        self._postgres = postgres
        self._redis = redis
