"""This module provides functionality to interact with limit data in database."""

import logging

from asyncpg import exceptions
from sqlalchemy import cast
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin
from app.models.mcc import MCCCategory
from app.utils.errors import SWSDatabaseError

LOGGER = logging.getLogger(__name__)


class Limit(db.Model, BaseModelMixin):
    """Class that represents budget category limits in system."""
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
    async def create_limit(cls, user_id, category_id, amount):
        """Create a new user`s budget category limit in database."""
        try:
            return await super().create(user_id=user_id, category_id=category_id, amount=amount)
        except exceptions.UniqueViolationError:
            raise SWSDatabaseError(f"Limit with that category for user={user_id} already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create limit category (%s) for user=%s. Error: %s", category_id, user_id, err)
            raise SWSDatabaseError("Failed to create limit budget category in database.")

    @classmethod
    async def get_user_limits(cls, user_id):
        """Retrieve user`s budget categories limits by user_id."""
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
            LOGGER.error("Couldn't retrieve budget categories limits for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to retrieve budget categories limits for user id {user_id}")

        return [dict(limit) for limit in limits]
