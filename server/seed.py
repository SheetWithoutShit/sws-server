"""This modules provides functionality in order to seed database."""

import asyncio

import gino

from app.config import POSTGRES_DSN
from migrations.data import insert_mcc_categories, insert_mccs


async def _get_db_connection():
    """Return gino db connection."""
    return await gino.Gino(POSTGRES_DSN)


async def seed_db():
    """Executes operations in order to seed database."""
    conn = await _get_db_connection()

    await conn.status(conn.text(insert_mcc_categories))
    await conn.status(conn.text(insert_mccs))


if __name__ == "__main__":
    asyncio.run(seed_db())
