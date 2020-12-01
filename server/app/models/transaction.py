"""This module provides functionality to interact with transactions in database."""

import logging
from datetime import datetime

from asyncpg import exceptions
from sqlalchemy import between, extract, func, cast
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError

from app.db import db
from app.models import BaseModelMixin
from app.models.mcc import MCC, MCCCategory
from app.cache import cache, MONTH_REPORT_CACHE_EXPIRE, MONTH_REPORT_CACHE_KEY
from app.utils.errors import DatabaseError


LOGGER = logging.getLogger(__name__)


class Transaction(db.Model, BaseModelMixin):
    """Class that represents Transaction in system."""
    __tablename__ = "transaction"

    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    balance = db.Column(db.Numeric(12, 2))
    cashback = db.Column(db.Numeric(12, 2), default=0)
    mcc = db.Column(db.Integer, db.ForeignKey("mcc.code"))
    timestamp = db.Column(db.DateTime, nullable=False)
    info = db.Column(db.String(255), nullable=False, default="")

    user = relationship("user", back_populates="transactions")

    _transaction_user_timestamp_idx = db.Index("transaction_user_timestamp_idx", "user_id", "timestamp")

    @classmethod
    async def create(cls, transaction):
        """Create a new transaction in database."""
        try:
            return await super().create(**transaction)
        except exceptions.UniqueViolationError:
            LOGGER.error("A transaction with that id already exists. Transaction: %s", transaction)
            raise DatabaseError("A transaction with such id already exists.")
        except SQLAlchemyError as err:
            LOGGER.error("Could not create transaction. Error: %s", err)
            raise DatabaseError("Failed to create a new transaction in database.")

    @classmethod
    async def create_bulk(cls, transactions):
        """Bulk create transactions."""
        for transaction in transactions:
            try:
                await cls.create(transaction)
            except DatabaseError:
                continue

    @classmethod
    async def get_transactions(cls, user_id, start_date, end_date):
        """Retrieve transactions for provided period by user_id."""
        try:
            transactions = await db \
                .select([
                    cls.id,
                    cls.user_id,
                    cast(cls.amount, db.String).label("amount"),
                    cast(cls.balance, db.String).label("balance"),
                    cast(cls.cashback, db.String).label("cashback"),
                    func.to_char(cls.timestamp, "YYYY.MM.DD HH24:MI:SS").label("timestamp"),
                    cls.mcc,
                    cls.info,
                    MCCCategory.name.label("category_name")
                ]) \
                .select_from(cls.join(MCC.join(MCCCategory))) \
                .where(
                    (cls.user_id == user_id) &
                    between(cls.timestamp, start_date, end_date)
                ) \
                .gino.all()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve transactions for user=%s. Error: %s", user_id, err)
            raise DatabaseError("Failed to retrieve transactions for requested user")

        return [dict(item) for item in transactions]

    @classmethod
    async def _get_month_report(cls, user_id, year, month):
        """Retrieve transaction report for specific month."""
        try:
            reports = await db \
                .select([
                    MCCCategory.name,
                    MCCCategory.info,
                    cast(func.abs(func.sum(cls.amount)), db.String).label("amount")
                ]) \
                .select_from(cls.join(MCC.join(MCCCategory))) \
                .where(
                    (cls.user_id == user_id) &
                    (cls.amount < 0) &
                    (extract("month", cls.timestamp) == month) &
                    (extract("year", cls.timestamp) == year)
                ) \
                .group_by(MCCCategory.name, MCCCategory.info) \
                .gino.all()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve month transaction report for user=%s. Error: %s", user_id, err)
            raise DatabaseError("Failed to retrieve monthly report for requested user.")

        return [dict(item) for item in reports]

    @classmethod
    async def get_month_report(cls, user_id, year, month):
        """Retrieve transaction from cache if not current month else from database."""
        today = datetime.today()
        current_month = today.year == year and today.month == month

        # no sense to cache for current month
        if current_month:
            return await cls._get_month_report(user_id, year, month)

        month_report_cache_key = MONTH_REPORT_CACHE_KEY.format(user_id=user_id, year=year, month=month)
        reports = await cache.get(month_report_cache_key)
        if not reports:
            reports = await cls._get_month_report(user_id, year, month)
            if not current_month and reports:
                await cache.set(month_report_cache_key, reports, MONTH_REPORT_CACHE_EXPIRE)

        return reports

    @classmethod
    async def get_daily_reports(cls, user_id, start_date, end_date):
        """Retrieve daily transactions reports for specific period of time."""
        try:
            reports = await db \
                .select([
                    func.date_trunc("day", cls.timestamp).label("date"),
                    cast(func.abs(func.sum(cls.amount)), db.String).label("amount")
                ]) \
                .select_from(cls) \
                .where(
                    (cls.user_id == user_id) &
                    (cls.amount < 0) &
                    (between(cls.timestamp, start_date, end_date))
                ) \
                .group_by("date") \
                .gino.all()
        except SQLAlchemyError as err:
            LOGGER.error("Could not retrieve daily transactions reports for user=%s. Error: %s", user_id, err)
            raise DatabaseError("Failed to retrieve daily transactions reports for requested user.")

        return reports
