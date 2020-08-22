"""This module provides helper functionality with time."""

from datetime import timedelta


DATE_FORMAT = "%Y.%m.%d"
DATETIME_FORMAT = "%Y.%m.%d %H:%M:%S"


def generate_days_period(start_date, end_date):
    """Yield days in provided date period."""
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    days_count = (end_date - start_date).days + 1
    for n_days in range(days_count):
        yield start_date + timedelta(days=n_days)
