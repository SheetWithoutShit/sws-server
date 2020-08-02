"""This module provides server app initialization."""

import asyncio
import logging

from aiohttp.web import Application
from core.database.postgres import PoolManager as PGPoolManager
from core.database.redis import PoolManager as RedisPoolManager

from app.auth.views import auth_routes
from app.budget.views import budget_routes
from app.profile.views import profile_routes
from app.transactions.views import transaction_routes

LOGGER = logging.getLogger(__name__)


async def init_clients(app):
    """Initialize aiohttp application with required clients."""
    app["postgres"] = postgres = await PGPoolManager.create()
    app["redis"] = redis = await RedisPoolManager.create()
    LOGGER.debug("Clients has successfully initialized.")

    yield

    await asyncio.gather(
        postgres.close(),
        redis.close()
    )
    LOGGER.debug("Clients has successfully closed.")


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    app.add_routes(auth_routes)
    app.add_routes(budget_routes)
    app.add_routes(profile_routes)
    app.add_routes(transaction_routes)

    app.cleanup_ctx.append(init_clients)

    return app