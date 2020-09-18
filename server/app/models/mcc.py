"""This module provides functionality to interact with MCC in database."""

import logging

from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.cache import cache, MCC_CODES_CACHE_KEY, MCC_CATEGORIES_CACHE_KEY
from app.models import BaseModelMixin
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class MCC(db.Model, BaseModelMixin):
    """Class that represents MCC in system."""
    __tablename__ = "mcc"

    code = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("mcc_category.id", ondelete="CASCADE"), nullable=False)

    category = relationship("mcc_category", back_populates="mccs")

    @classmethod
    async def get_codes(cls):
        """Retrieve all MCC codes."""
        mcc_codes = await cache.get(MCC_CODES_CACHE_KEY)
        if mcc_codes:
            return mcc_codes
        try:
            mcc_codes = [mcc.code for mcc in await cls.query.gino.all()]
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve all MCC. Error: %s", err)
            raise SWSDatabaseError("Failed to retrieve all MCC.")
        else:
            await cache.set(MCC_CODES_CACHE_KEY, mcc_codes)

        return mcc_codes


class MCCCategory(db.Model, BaseModelMixin):
    """Class that represents MCC category in system."""
    __tablename__ = "mcc_category"

    id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    info = db.Column(db.String(255), nullable=False, default="")

    mccs = relationship("mcc", back_populates="category")

    @classmethod
    async def get_categories(cls):
        """Retrieve all existing mcc categories."""
        mcc_categories = await cache.get(MCC_CATEGORIES_CACHE_KEY)
        if mcc_categories:
            return mcc_categories
        try:
            mcc_categories = [mcc.name for mcc in await cls.query.gino.all()]
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve all MCC categories. Error: %s", err)
            raise SWSDatabaseError("Failed to retrieve all MCC categories.")
        else:
            await cache.set(MCC_CATEGORIES_CACHE_KEY, mcc_categories)

        return mcc_categories

    @classmethod
    async def get_by_name(cls, name):
        """Return queried limit by provided name."""
        try:
            category = await cls.query.where(cls.name == name).gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve MCC category by name=%s. Error: %s", name, err)
            raise SWSDatabaseError(f"Failed to retrieve MCC category by name={name}")

        if not category:
            raise SWSDatabaseError(f"The category '{name}' does not exist.")

        return category
