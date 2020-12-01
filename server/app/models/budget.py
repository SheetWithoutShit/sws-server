"""This module provides functionality to interact with budget data in database."""

import logging

from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin, parse_status
from app.utils.errors import DatabaseError

LOGGER = logging.getLogger(__name__)


class Budget(db.Model, BaseModelMixin):
    """Class that represents Budget in system."""
    __tablename__ = "budget"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    income = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    savings = db.Column(db.SmallInteger, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    user = relationship("user", back_populates="budget")

    _budget_user_idx = db.Index("budget_user_idx", "user_id")

    @classmethod
    async def get_budget(cls, user_id):
        """Retrieve queried budget from database by provided user_id."""
        try:
            budget = await cls.query \
                .where(cls.user_id == user_id) \
                .gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve budget for user=%s. Error: %s", user_id, err)
            raise DatabaseError("Failed to retrieve budget for requested user.")

        return budget

    @classmethod
    async def update_budget(cls, user_id, savings, income):
        """Update profile budget in database for provided user."""
        try:
            status, _ = await cls.update \
                .values(savings=savings, income=income)\
                .where(cls.user_id == user_id) \
                .gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Could not update budget for user=%s. Error: %s", user_id, err)
            raise DatabaseError("Failed to update budget for requested user.")

        updated = parse_status(status)
        if not updated:
            raise DatabaseError("The requested user`s budget was not updated.")
