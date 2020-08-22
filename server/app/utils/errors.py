"""This module provides custom errors."""


class SWSError(Exception):
    """Class that represents base SWS error."""


class SWSDatabaseError(SWSError):
    """Class that represents errors caused on interaction with database."""


class SWSTokenError(SWSError):
    """Class that represents errors caused on interaction with auth token."""
