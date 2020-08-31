"""This module provides functionality to interact with MCC in database."""

import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class MCC(db.Model, BaseModelMixin):
    """Class that represents MCC in system."""
    __tablename__ = "mcc"

    code = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    info = db.Column(db.String)

    @classmethod
    async def get_all(cls):
        """Retrieve all MCC instances."""
        # TODO: implement caching since it is the same all time
        try:
            mccs = await cls.query.gino.all()
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't retrieve all MCC. Error: %s", err)
            raise SWSDatabaseError("Failed to retrieve all MCC.")

        return mccs
