"""This module provides server app initialization."""

import logging

import jinja2
import aiohttp_jinja2
import requests
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
    if config.SERVER_MODE == "dev":
        response = requests.get("http://ngrok:4040/api/tunnels").json()
        _, http = response["tunnels"]
        ngrok_domain = http["public_url"]
        LOGGER.debug("NGROK forwarding collector domain to: %s", ngrok_domain)
        config.COLLECTOR_HOST = ngrok_domain

    setattr(app, "config", config)
    LOGGER.debug("Application config has successfully set up.")


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    db.init_app(
        app,
        dict(
            dsn=config.POSTGRES_DSN,
            min_size=config.POSTGRES_POOL_MIN_SIZE,
            max_size=config.POSTGRES_POOL_MAX_SIZE,
            retry_limit=config.POSTGRES_RETRY_LIMIT,
            retry_interval=config.POSTGRES_RETRY_INTERVAL,
        ),
    )

    aiojobs_setup(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(config.TEMPLATES_DIR))

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
