"""This module provides server app initialization."""

import os
import asyncio
import logging

from aiohttp.web import Application
from core.database.postgres import PoolManager as PGPoolManager
from core.database.redis import PoolManager as RedisPoolManager

from app.middlewares import auth_middleware, body_validator_middleware
from app.user.db import User
from app.user.views.auth import auth_views
from app.user.views.profile import profile_routes
from app.budget.db import Budget
from app.budget.views import budget_routes
from app.transactions.db import Transaction
from app.transactions.views import transaction_routes

LOGGER = logging.getLogger(__name__)


async def init_clients(app):
    """Initialize aiohttp application with required clients."""
    app["postgres"] = postgres = await PGPoolManager.create()
    app["redis"] = redis = await RedisPoolManager.create()

    app["user"] = User(postgres=postgres)
    app["transaction"] = Transaction(postgres=postgres)
    app["budget"] = Budget(postgres=postgres)
    LOGGER.debug("Clients has successfully initialized.")

    yield

    await asyncio.gather(
        postgres.close(),
        redis.close()
    )
    LOGGER.debug("Clients has successfully closed.")


async def init_constants(app):
    """Initialize aiohttp application with required constants."""
    # TODO: Load from file
    app["constants"] = constants = {}

    constants["SERVER_SECRET"] = os.environ["SERVER_SECRET"]


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    app.add_routes(auth_views)
    app.add_routes(budget_routes)
    app.add_routes(profile_routes)
    app.add_routes(transaction_routes)

    app.cleanup_ctx.append(init_clients)
    app.on_startup.append(init_constants)

    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(auth_middleware)

    return app
