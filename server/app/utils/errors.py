"""This module provides custom errors."""


class BaseError(Exception):
    """Class that represents base error."""

    def __init__(self, message=None):
        """Initialize base custom error."""
        super().__init__()
        self.message = message

    def __str__(self):
        """Return message for str method."""
        return self.message

    def __repr__(self):
        """Return message for repr method."""
        return self.message


class TokenError(BaseError):
    """Class that represents errors caused on interaction with auth token."""


class RetryError(BaseError):
    """Class that represents errors caused for retry."""


class DatabaseError(BaseError):
    """Class that represents errors caused on interaction with database."""


class DBNoResultFoundError(DatabaseError):
    """Class that represents errors caused on not existing entity."""
