"""This modules provides functionality in order to seed database."""

import asyncio
import argparse
import random
from datetime import datetime, timedelta

import gino

from app.config import POSTGRES_DSN
from app.models.user import User


DATABASE_ENVS = ["prod", "dev"]

MCC_IDS = [-1, 2741, 7829, 5811, 4121, 5451, 5172, 5697, 5733]
USER_EMAIL = "test@example.com"
USER_PASSWORD = User.generate_password_hash("Test1234!")
USER_ID = 1234567890

CREATE_USER_QUERY = f"""
    INSERT INTO "user" (id, email, password, first_name, last_name, notifications_enabled, monobank_token) 
    VALUES ({USER_ID}, {USER_EMAIL}, '{USER_PASSWORD}', 'Test', 'User', true, 'testmonobanktoken')
"""
CREATE_TRANSACTION_QUERY = """
    INSERT INTO transaction (id, user_id, amount, balance, cashback, mcc, timestamp, info)
    VALUES (:id, :user_id, :amount, :balance, :cashback, :mcc, :timestamp, 'testtransaction')
"""


async def _get_db_connection():
    """Return gino db connection."""
    return await gino.Gino(POSTGRES_DSN)


async def seed_dev_db():
    """Executes operations in order to seed dev database."""
    conn = await _get_db_connection()
    today = datetime.today()

    await conn.status(conn.text(CREATE_USER_QUERY))

    balance = 0
    for i in range(500):
        mcc = random.choice(MCC_IDS)
        timestamp = today - timedelta(hours=i * 3)
        amount = random.randint(-1000, 1000)
        balance = balance + amount
        cashback = random.randint(1, 50)

        await conn.status(
            conn.text(CREATE_TRANSACTION_QUERY),
            id=str(USER_ID + i),
            user_id=USER_ID,
            amount=amount,
            balance=balance,
            cashback=cashback,
            timestamp=timestamp,
            mcc=mcc
        )


async def seed_prod_db():
    """Executes operations in order to seed prod database."""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Seed prod/dev database.')
    parser.add_argument("--env", required=True, type=str, choices=DATABASE_ENVS)

    args = parser.parse_args()
    if args.env == "prod":
        asyncio.run(seed_prod_db())
    elif args.env == "dev":
        asyncio.run(seed_dev_db())
