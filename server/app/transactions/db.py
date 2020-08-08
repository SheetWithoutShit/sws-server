"""This module provides functionality to interact with transactions in database."""

import logging

from asyncpg import exceptions


LOGGER = logging.getLogger(__name__)


class Transaction:
    """Model that provides methods to work with user`s transactions."""

    GET_TRANSACTIONS = """
        SELECT *, amount::varchar, balance::varchar, cashback::varchar, timestamp::varchar 
        FROM "TRANSACTION"
        WHERE user_id = $1
            and timestamp between $2 and $3
    """

    def __init__(self, postgres=None):
        """Initialize transaction instance with required database clients."""
        self._postgres = postgres

    async def get_transactions(self, user_id, start_date, end_date):
        """Retrieve transactions from database for provided user_id."""
        try:
            records = await self._postgres.fetch(self.GET_TRANSACTIONS, user_id, start_date, end_date)
            return [dict(x) for x in records]
        except (exceptions.PostgresError, AttributeError) as err:
            LOGGER.error("Couldn't retrieve transactions for user=%s. Error: %s", user_id, err)
