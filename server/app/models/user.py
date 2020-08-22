"""This module provides functionality to interact with user data in database."""

import logging

import bcrypt
from asyncpg import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin
from app.utils.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)
HASH_SALT_ROUNDS = 12


class User(db.Model, BaseModelMixin):
    """Class that represents User in system."""
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False, default="")
    last_name = db.Column(db.String(255), nullable=False, default="")
    telegram_id = db.Column(db.Integer)
    notifications_enabled = db.Column(db.Boolean, nullable=False, default=False)
    monobank_token = db.Column(db.String(255), nullable=False, default="")

    @staticmethod
    def generate_password_hash(password):
        """Return generated hash for provided password."""
        password_bin = password.encode("utf-8")
        password_hash = bcrypt.hashpw(password_bin, bcrypt.gensalt(HASH_SALT_ROUNDS))
        return password_hash.decode("utf-8")

    def check_password_hash(self, password):
        """Check if provided passwords are equal."""
        password_hash_bin = self.password.encode("utf-8")
        password_bin = password.encode("utf-8")
        return bcrypt.checkpw(password_bin, password_hash_bin)

    @classmethod
    async def create(cls, email, password):
        """Create a new user in database."""
        password_hash = User.generate_password_hash(password)
        try:
            return await super().create(email=email, password=password_hash)
        except exceptions.UniqueViolationError:
            raise SWSDatabaseError(f"A user with that email address already exists: {email}.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create user=%s. Error: %s", email, err)
            raise SWSDatabaseError("Failed to create a new user in database.")

    @classmethod
    async def get_by_email(cls, email):
        """Return queried user by provided email."""
        try:
            user = await User.query.where(User.email == email).gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Could not create user=%s. Error: %s", email, err)
            raise SWSDatabaseError("Failed to create a new user in database.")

        if not user:
            raise SWSDatabaseError(f"A user with this email does not exist: {email}.")

        return user
