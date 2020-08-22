"""This module provides functionality to interact with budget data in database."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin, parse_status
from app.utils.errors import SWSDatabaseError

LOGGER = logging.getLogger(__name__)


class Budget(db.Model, BaseModelMixin):
    """Class that represents Budget in system."""
    __tablename__ = "budget"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    income = db.Column(db.Numeric(12, 2), default=0.0)
    savings = db.Column(db.SmallInteger, default=0)
    year = db.Column(db.SmallInteger, nullable=False)
    month = db.Column(db.SmallInteger, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    _budget_user_idx = db.Index("budget_user_idx", "user_id", "month", "year")

    @classmethod
    async def get_budget(cls, user_id, year, month):
        """Retrieve queried budget from database by provided user_id."""
        try:
            budget = await cls.query \
                .where(
                    (cls.user_id == user_id) &
                    (cls.year == year) &
                    (cls.month == month)) \
                .gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve budget for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to retrieve budget for user id {user_id}")

        if not budget:
            raise SWSDatabaseError(f"A budget for user={user_id} in this period ({month}.{year}) does not exist.")

        return budget

    @classmethod
    async def update_budget(cls, user_id, year, month, savings, income):
        """Update profile budget in database for provided user."""
        try:
            status, _ = await cls.update \
                .values(savings=savings, income=income)\
                .where(
                    (cls.user_id == user_id) &
                    (cls.year == year) &
                    (cls.month == month)) \
                .gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve budget for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to retrieve budget for user id {user_id}")

        updated = parse_status(status)
        if not updated:
            raise SWSDatabaseError("The user`s budget was not updated.")
