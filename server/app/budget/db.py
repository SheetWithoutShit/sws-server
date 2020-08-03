"""This module provides functionality to interact with budget data in database."""

import logging

from asyncpg import exceptions


LOGGER = logging.getLogger(__name__)


class Budget:
    """Model that provides methods to work with user`s data."""

    GET_BUDGET = """
        SELECT *, income::varchar
        FROM "BUDGET"
        WHERE user_id = $1
            and year = $2
            and month = $3
    """
    UPDATE_BUDGET = """
        UPDATE "BUDGET"
        SET savings = COALESCE($4, savings),
            income = COALESCE($5, income)
        WHERE user_id = $1
            and year = $2
            and month = $3
    """

    def __init__(self, postgres=None):
        """Initialize budget instance with required clients."""
        self._postgres = postgres

    async def get_budget(self, user_id, year, month):
        """Retrieve budget from database for provided user_id."""
        try:
            record = await self._postgres.fetchone(self.GET_BUDGET, user_id, year, month)
            return dict(record.items())
        except (exceptions.PostgresError, AttributeError) as err:
            LOGGER.error("Couldn't retrieve budget for user=%s. Error: %s", user_id, err)

    async def update_budget(self, user_id, year, month, data):
        """Update budget in database for provided user."""
        update_args = (
            data.get("savings"),
            data.get("income"),
        )
        try:
            return await self._postgres.execute(self.UPDATE_BUDGET, user_id, year, month, *update_args)
        except exceptions.PostgresError as err:
            LOGGER.error("Could not update budget fro user=%s. Error: %s", user_id, err)
