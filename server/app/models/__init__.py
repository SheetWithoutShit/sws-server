"""This module provides functionality for database interactions."""

from decimal import Decimal
from datetime import datetime

from app.utils.time import DATETIME_FORMAT


class BaseModelMixin:
    """Mixin that provides base model helper functionality."""

    hidden_columns = None

    def as_dict(self):
        """Return instance information in dictionary format."""
        result = {}
        for column in self.__table__.columns:
            column_name = column.name
            if self.hidden_columns and column_name in self.hidden_columns:
                continue

            value = getattr(self, column_name)
            if isinstance(value, Decimal):
                value = str(value)

            if isinstance(value, datetime):
                value = value.strftime(DATETIME_FORMAT)

            result[column_name] = value

        return result


def parse_status(status):
    """Parse gino database status."""
    if isinstance(status, str):
        _, status_count = status.split(" ")
        return bool(int(status_count))

    return False
