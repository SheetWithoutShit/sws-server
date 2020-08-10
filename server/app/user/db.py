"""This module provides functionality to interact with user data in database."""

import os
import logging

from asyncpg import exceptions
import bcrypt

from app.errors import SWSDatabaseError


LOGGER = logging.getLogger(__name__)


class User:
    """Model that provides methods to work with user data."""

    HASH_SALT_ROUNDS = 14

    INSERT_USER = """
        INSERT INTO "USER" (email, password)
        VALUES ($1, $2)
        RETURNING id
    """

    GET_USER_BY_EMAIL = """
        SELECT *
        FROM "USER"
        WHERE email=$1
    """

    GET_PROFILE_BUDGET = """
        SELECT *, income::varchar
        FROM "BUDGET"
        WHERE user_id = $1
            and year = $2
            and month = $3
    """
    UPDATE_PROFILE_BUDGET = """
        UPDATE "BUDGET"
        SET savings = COALESCE($4, savings),
            income = COALESCE($5, income)
        WHERE user_id = $1
            and year = $2
            and month = $3
    """

    def __init__(self, postgres=None):
        """Initialize user instance with required database clients."""
        self._postgres = postgres
        self.secret_key = os.environ["SERVER_SECRET"]
        self.jwt_exp_days = os.environ.get("JWT_EXP_DAYS", 7)
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

    def generate_password_hash(self, password):
        """Return generated hash for provided password."""
        password_bin = password.encode("utf-8")
        password_hash = bcrypt.hashpw(password_bin, bcrypt.gensalt(self.HASH_SALT_ROUNDS))
        return password_hash.decode("utf-8")

    def check_password_hash(self, password_hash, password):  #pylint: disable=no-self-use
        """Check if provided passwords are equal."""
        password_hash_bin = password_hash.encode("utf-8")
        password_bin = password.encode("utf-8")
        return bcrypt.checkpw(password_bin, password_hash_bin)

    async def create_user(self, email, password):
        """Create a new user in database.."""
        password_hash = self.generate_password_hash(password)
        try:
            user = await self._postgres.fetchone(self.INSERT_USER, email, password_hash)
            return dict(user)
        except exceptions.UniqueViolationError:
            raise SWSDatabaseError(f"A user with that email address already exists: {email}.")
        except exceptions.PostgresError as err:
            LOGGER.error("Could not create user=%s. Error: %s", email, err)
            raise SWSDatabaseError("Failed to create a new user in database.")

    async def get_user_by_email(self, email):
        """Retrieve user from database by provided email."""
        try:
            record = await self._postgres.fetchone(self.GET_USER_BY_EMAIL, email)
            return dict(record)
        except TypeError:
            raise SWSDatabaseError(f"A user with this email does not exist: {email}.")
        except exceptions.PostgresError as err:
            LOGGER.error("Could not retrieve user=%s. Error: %s", email, err)
            raise SWSDatabaseError(f"Failed to retrieve user {email} from database.")

    async def get_profile_budget(self, user_id, year, month):
        """Retrieve profile budget from database for provided user_id."""
        try:
            record = await self._postgres.fetchone(self.GET_PROFILE_BUDGET, user_id, year, month)
            return dict(record)
        except (exceptions.PostgresError, AttributeError) as err:
            LOGGER.error("Couldn't retrieve profile budget for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to retrieve profile budget for user id {user_id}")

    async def update_profile_budget(self, user_id, year, month, data):
        """Update profile budget in database for provided user."""
        update_args = (
            data.get("savings"),
            data.get("income"),
        )
        try:
            return await self._postgres.execute(self.UPDATE_PROFILE_BUDGET, user_id, year, month, *update_args)
        except exceptions.PostgresError as err:
            LOGGER.error("Could not update profile budget for user=%s. Error: %s", user_id, err)
            raise SWSDatabaseError(f"Failed to update profile budget for user id {user_id}")
