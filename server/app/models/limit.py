"""This module provides functionality to interact with limit data in database."""

import logging

from sqlalchemy.orm import relationship

from app.db import db
from app.models import BaseModelMixin

LOGGER = logging.getLogger(__name__)


class Limit(db.Model, BaseModelMixin):
    """Class that represents budget limits in system."""
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
