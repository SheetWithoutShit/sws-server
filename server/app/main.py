"""This module provides server app initialization."""

import os
import logging

import jinja2
import aiohttp_jinja2
import requests
from aiogram.dispatcher import webhook
from aiohttp.web import Application
from aiojobs.aiohttp import setup as aiojobs_setup
from aiohttp_swagger import setup_swagger

from app import config
from app.db import db, get_database_dsn
from app.telegram import TELEGRAM_BOT, TELEGRAM_DISPATCHER
from app.middlewares import auth_middleware, body_validator_middleware, error_middleware
from app.api.index import internal_routes
from app.api.budget import budget_routes
from app.api.auth import auth_routes
from app.api.user import user_routes
from app.api.limit import limit_routes
from app.api.transaction import transaction_routes
from app.api.telegram import handle_start, handle_stop
from app.api.index import handle_404, handle_405, handle_500


LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s - %(levelname)s: %(name)s: %(message)s"


async def init_config(app):
    """Initialize aiohttp application with required constants."""
    if config.SERVER_MODE == "DEV":
        response = requests.get("http://ngrok:4040/api/tunnels").json()
        _, http = response["tunnels"]
        ngrok_domain = http["public_url"]
        LOGGER.debug("NGROK forwarding collector domain to: %s", ngrok_domain)
        config.COLLECTOR_HOST = ngrok_domain

    setattr(app, "config", config)
    LOGGER.debug("Application config has successfully set up.")


def init_logging():
    """
    Initialize logging stream with info level to console and
    create file logger with info level if permission to file allowed.
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

    # disabling gino postgres echo logs
    # in order to set echo pass echo=True to db config dict
    logging.getLogger("gino.engine._SAEngine").propagate = False

    log_dir = os.getenv("LOG_DIR")
    log_filepath = f"{log_dir}/server.log"
    if log_dir and os.path.isdir(log_dir) and os.access(log_dir, os.W_OK):
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logging.getLogger("").addHandler(file_handler)


def init_db(app):
    """Initialize database postgres connection based on server mode."""
    db.init_app(
        app,
        dict(
            dsn=get_database_dsn(),
            min_size=config.POSTGRES_POOL_MIN_SIZE,
            max_size=config.POSTGRES_POOL_MAX_SIZE,
            retry_limit=config.POSTGRES_RETRY_LIMIT,
            retry_interval=config.POSTGRES_RETRY_INTERVAL
        ),
    )


async def init_telegram_webhook(app):
    """Initialize telegram bot webhook."""
    telegram_webhook = await TELEGRAM_BOT.get_webhook_info()
    if telegram_webhook.url != config.TELEGRAM_BOT_WEBHOOK_URL:
        await TELEGRAM_BOT.delete_webhook()
        await TELEGRAM_BOT.set_webhook(config.TELEGRAM_BOT_WEBHOOK_URL)

    webhook.configure_app(TELEGRAM_DISPATCHER, app, config.TELEGRAM_BOT_WEBHOOK_PATH)
    LOGGER.debug("Telegram webhook has successfully set up.")

    yield

    await TELEGRAM_BOT.delete_webhook()
    LOGGER.debug("Telegram webhook has successfully deleted.")


def init_swagger(app):
    """Initialize swagger documentation for the server application."""
    swagger_path = os.path.join(config.ROOT_DIR, "swagger.yaml")
    setup_swagger(
        app,
        swagger_url="/v1/api",
        ui_version=2,
        swagger_from_file=swagger_path
    )


def init_app():
    """Prepare aiohttp web server for further running."""
    app = Application()

    init_logging()
    init_db(app)
    init_swagger(app)

    aiojobs_setup(app)
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(config.TEMPLATES_DIR))

    app.add_routes(auth_routes)
    app.add_routes(budget_routes)
    app.add_routes(transaction_routes)
    app.add_routes(internal_routes)
    app.add_routes(user_routes)
    app.add_routes(limit_routes)

    TELEGRAM_DISPATCHER.register_message_handler(handle_start, commands=["start"])
    TELEGRAM_DISPATCHER.register_message_handler(handle_stop, commands=["stop"])

    app.on_startup.append(init_config)

    if config.SERVER_MODE != "DEV":
        app.cleanup_ctx.append(init_telegram_webhook)

    app.middlewares.append(db)
    app.middlewares.append(error_middleware({
        404: handle_404,
        405: handle_405,
        500: handle_500
    }))
    app.middlewares.append(body_validator_middleware)
    app.middlewares.append(auth_middleware)

    return app
