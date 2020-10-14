"""This module provides functionality to interact with user data in database."""

import logging

import bcrypt
from asyncpg import exceptions
from sqlalchemy import func
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin, parse_status
from app.utils.errors import DatabaseError


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
    created = db.Column(db.DateTime, nullable=False, default=func.now())

    budget = relationship("budget", back_populates="user", uselist=False)
    transactions = relationship("transaction", back_populates="user")
    limits = relationship("limit", back_populates="user")

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
    async def get_by_id(cls, user_id):
        """Return queried user by provided id."""
        try:
            user = await cls.get(user_id)
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve user=%s. Error: %s", user_id, err)
            raise DatabaseError(f"Failure. Failed to retrieve user={user_id}")

        if not user:
            raise DatabaseError(f"Failure. The user={user_id} does not exist.")

        return user

    @classmethod
    async def get_by_email(cls, email):
        """Return queried user by provided email."""
        try:
            user = await cls.query.where(User.email == email).gino.first()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve user=%s. Error: %s", email, err)
            raise DatabaseError(f"Failure. Failed to retrieve user={email}")

        if not user:
            raise DatabaseError(f"Failure. The user={email} does not exist.")

        return user

    @classmethod
    async def create(cls, email, password):
        """Create a new user in database."""
        try:
            return await super().create(email=email, password=password)
        except exceptions.UniqueViolationError:
            raise DatabaseError(f"Failure. A user with email={email} already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create user=%s. Error: %s", email, err)
            raise DatabaseError("Failure. Failed to create a new user in database.")

    @classmethod
    async def update(cls, user_id, **kwargs):
        """Update user instance in database by user_id."""
        try:
            status, _ = await super().update \
                .values(**kwargs) \
                .where(cls.id == user_id) \
                .gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Could not update user=%s. Error: %s", user_id, err)
            raise DatabaseError(f"Failure. Failed to update user={user_id}")

        updated = parse_status(status)
        if not updated:
            raise DatabaseError(f"Failure. The user={user_id} was not updated.")

    @classmethod
    async def delete(cls, user_id):
        """Delete user instance by provided id."""
        try:
            status, _ = await super().delete.where(cls.id == user_id).gino.status()
        except SQLAlchemyError as err:
            LOGGER.error("Could not delete user=%s. Error: %s", user_id, err)
            raise DatabaseError(f"Failure. Failed to delete user={user_id}")

        deleted = parse_status(status)
        if not deleted:
            raise DatabaseError(f"Failure. The user={user_id} was not deleted.")
