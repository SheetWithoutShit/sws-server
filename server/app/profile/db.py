"""This module provides functionality to interact with user profile data in database."""

import logging

from asyncpg import exceptions

from app.db import DB


LOGGER = logging.getLogger(__name__)


class UserProfile(DB):
    """Model that provides methods to work with user`s profile."""

    GET_PROFILE_BUDGET = """
        SELECT *, income::varchar
        FROM "BUDGET"
        WHERE user_id = $1
            and year = $2
            and month = $3
    """
    UPDATE_PROFILE_BUDGET = """
        UPDATE "BUDGET"
        SET savings = COALESCE($4, savings),
            income = COALESCE($5, income)
        WHERE user_id = $1
            and year = $2
            and month = $3
    """

    async def get_profile_budget(self, user_id, year, month):
        """Retrieve profile budget from database for provided user_id."""
        try:
            record = await self._postgres.fetchone(self.GET_PROFILE_BUDGET, user_id, year, month)
            return dict(record.items())
        except (exceptions.PostgresError, AttributeError) as err:
            LOGGER.error("Couldn't retrieve profile budget for user=%s. Error: %s", user_id, err)

    async def update_profile_budget(self, user_id, year, month, data):
        """Update profile budget in database for provided user."""
        update_args = (
            data.get("savings"),
            data.get("income"),
        )
        try:
            return await self._postgres.execute(self.UPDATE_PROFILE_BUDGET, user_id, year, month, *update_args)
        except exceptions.PostgresError as err:
            LOGGER.error("Could not update profile budget for user=%s. Error: %s", user_id, err)
