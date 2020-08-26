"""This module provides functionality to interact with user data in database."""

import logging

import bcrypt
from asyncpg import exceptions
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin, parse_status
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

    private_columns = ["password", "monobank_token"]

    def as_dict(self):
        """Return user instance information in dictionary format."""
        user_dict = super().as_dict()
        user_dict["monobank_enabled"] = bool(self.monobank_token)

        return user_dict

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
    async def create_user(cls, email, password):
        """Create a new user in database."""
        try:
            return await super().create(email=email, password=password)
        except exceptions.UniqueViolationError:
            raise SWSDatabaseError(f"A user with that email address already exists: {email}.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create user=%s. Error: %s", email, err)
            raise SWSDatabaseError("Failed to create a new user in database.")

    @classmethod
    async def update_user(cls, user_id, **kwargs):
        """Update user instance in database by user_id."""
        try:
            status, _ = await cls.update \
                .values(**kwargs) \
                .where(cls.id == user_id) \
                .gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Couldn't update user with id=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to update user with id={user_id}")

        updated = parse_status(status)
        if not updated:
            raise SWSDatabaseError("The user was not updated.")

    @classmethod
    async def get_by_id(cls, id_):
        """Return queried user by provided id."""
        try:
            user = await cls.get(id_)
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve user by id=%s. Error: %s", id_, err)
            raise SWSDatabaseError(f"Failed to retrieve user by id={id_}")

        if not user:
            raise SWSDatabaseError(f"A user with this id does not exist: {id_}.")

        return user

    @classmethod
    async def get_by_email(cls, email):
        """Return queried user by provided email."""
        try:
            user = await User.query.where(User.email == email).gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve user by email=%s. Error: %s", email, err)
            raise SWSDatabaseError(f"Failed to retrieve user by email={email}")

        if not user:
            raise SWSDatabaseError(f"A user with this email does not exist: {email}.")

        return user
