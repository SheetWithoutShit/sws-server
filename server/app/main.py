"""This module provides server app initialization."""

import logging

from aiohttp.web import Application
from aiojobs.aiohttp import setup as aiojobs_setup

from app import config
from app.db import db
from app.middlewares import auth_middleware, body_validator_middleware, error_middleware
from app.api.index import internal_routes
from app.api.budget import budget_routes
from app.api.auth import auth_routes
from app.api.user import user_routes
from app.api.transaction import transaction_routes
from app.api.index import handle_404, handle_405, handle_500


LOGGER = logging.getLogger(__name__)


async def init_config(app):
    """Initialize aiohttp application with required constants."""
    setattr(app, "config", config)


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    db.init_app(app, {"dsn": config.POSTGRES_DSN})

    aiojobs_setup(app)

    app.add_routes(auth_routes)
    app.add_routes(budget_routes)
    app.add_routes(transaction_routes)
    app.add_routes(internal_routes)
    app.add_routes(user_routes)

    app.on_startup.append(init_config)

    app.middlewares.append(db)
    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_middleware({
        404: handle_404,
        405: handle_405,
        500: handle_500
    }))

    return app
