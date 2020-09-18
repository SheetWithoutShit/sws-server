"""This module provides functionality to interact with limit data in database."""

import logging

from asyncpg import exceptions
from sqlalchemy import cast
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin, parse_status
from app.models.mcc import MCCCategory
from app.utils.errors import SWSDatabaseError

LOGGER = logging.getLogger(__name__)


class Limit(db.Model, BaseModelMixin):
    """Class that represents Budget Limit in system."""
    __tablename__ = "limit"
    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', name='unique_user_category'),
    )

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("mcc_category.id"), nullable=False)

    user = relationship("user", back_populates="limits")

    _limit_user_idx = db.Index("limit_user_idx", "user_id")

    @classmethod
    async def get(cls, limit_id):
        """Return queried budget limit by provided id."""
        try:
            limit = await super().get(limit_id)
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve budget limit by id=%s. Error: %s", limit_id, err)
            raise SWSDatabaseError(f"Failure. Failed to retrieve budget limit={limit_id}.")

        if not limit:
            raise SWSDatabaseError(f"Failure. The budget limit with id={limit_id} does not exist.")

        return limit

    @classmethod
    async def get_user_limits(cls, user_id):
        """Return queried user`s budget limits."""
        try:
            limits = await db \
                .select([
                    cls.id,
                    cast(cls.amount, db.String).label("amount"),
                    MCCCategory.name,
                    MCCCategory.info,
                ]) \
                .select_from(cls.join(MCCCategory)) \
                .where(cls.user_id == user_id) \
                .gino.all()

        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve budget limits for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failure. Failed to retrieve budget limits for user={user_id}.")

        return [dict(limit) for limit in limits]

    @classmethod
    async def create(cls, user_id, category_id, amount):
        """Create a new budget limit in database."""
        try:
            return await super().create(user_id=user_id, category_id=category_id, amount=amount)
        except exceptions.UniqueViolationError:
            raise SWSDatabaseError(f"Failure. Limit with that category for user={user_id} already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create limit with category=%s for user=%s. Error: %s", category_id, user_id, err)
            raise SWSDatabaseError(f"Failure. Failed to create limit budget for user={user_id}.")

    @classmethod
    async def update(cls, limit_id, amount):
        """Update budget limit instance in database."""
        try:
            status, _ = await super().update \
                .values(amount=amount) \
                .where(cls.id == limit_id) \
                .gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Could not update budget limit=%s. Error: %s", limit_id, err)
            raise SWSDatabaseError(f"Failure. Failed to update budget limit={limit_id}")

        updated = parse_status(status)
        if not updated:
            raise SWSDatabaseError(f"Failure. The budget limit={limit_id} was not updated.")

    @classmethod
    async def delete(cls, limit_id):
        """Delete budget limit by provided id."""
        try:
            status, _ = await super().delete.where(cls.id == limit_id).gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Could not delete budget limit by id=%s. Error: %s", limit_id, err)
            raise SWSDatabaseError(f"Failure. Failed to delete budget limit={limit_id}")

        deleted = parse_status(status)
        if not deleted:
            raise SWSDatabaseError(f"Failure. The budget category limit={limit_id} was not deleted.")
