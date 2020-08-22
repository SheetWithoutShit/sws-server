"""This module provides functionality to interact with MCC in database."""

from app.db import db
from app.models import BaseModelMixin


class MCC(db.Model, BaseModelMixin):
    """Class that represents MCC in system."""
    __tablename__ = "mcc"

    code = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(255), nullable=False)
    info = db.Column(db.String)
