"""This module provides custom errors."""


class SWSError(Exception):
    """Class that represents base SWS error."""

    def __init__(self, message=None):
        """Initialize SWS custom error."""
        super().__init__()
        self.message = message

    def __str__(self):
        """Return message for str method."""
        return self.message

    def __repr__(self):
        """Return message for repr method."""
        return self.message


class SWSDatabaseError(SWSError):
    """Class that represents errors caused on interaction with database."""


class SWSTokenError(SWSError):
    """Class that represents errors caused on interaction with auth token."""


class SWSRetryError(SWSError):
    """Class that represents errors caused for retry."""
