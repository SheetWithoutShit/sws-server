"""This module provides functionality to interact with budget data in database."""

import logging

from asyncpg import exceptions

from app.db import DB


LOGGER = logging.getLogger(__name__)


class Budget(DB):
    """Model that provides methods to work with user`s profile."""

    GET_MONTH_BUDGET = """
        SELECT mcc, mcc_table.category, mcc_table.info, ABS(SUM(amount))::varchar as amount
        FROM "TRANSACTION"
        LEFT JOIN "MCC" as mcc_table on mcc=code
        WHERE user_id=$1
            and amount >= 0
            and EXTRACT(YEAR FROM timestamp) = $2
            and EXTRACT(MONTH FROM timestamp) = $3
        GROUP BY mcc, mcc_table.category, mcc_table.info
    """

    GET_DAILY_BUDGETS = """
        SELECT date_trunc('DAY', timestamp) as date, ABS(SUM(amount))::varchar as amount
        FROM "TRANSACTION"
        WHERE user_id=$1
            and amount < 0
            and timestamp between $2 and $3
        GROUP BY date
    """

    async def get_month_budget(self, user_id, year, month):
        """Retrieve user budget information for specific month."""
        try:
            records = await self._postgres.fetch(self.GET_MONTH_BUDGET, user_id, year, month)
            return [dict(x) for x in records]
        except exceptions.PostgresError as err:
            LOGGER.error("Couldn't retrieve budget for user=%s. Error: %s", user_id, err)

    async def get_daily_budgets(self, user_id, start_date, end_date):
        """Retrieve daily budgets reports for specific period of time."""
        try:
            records = await self._postgres.fetch(self.GET_DAILY_BUDGETS, user_id, start_date, end_date)
            return [dict(x) for x in records]
        except exceptions.PostgresError as err:
            LOGGER.error("Couldn't retrieve daily budgets for user=%s. Error: %s", user_id, err)
