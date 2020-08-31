"""This module provides config variables for server app."""

import os

from sqlalchemy.engine.url import URL


# Server stuff
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
SERVER_MODE = os.getenv("SERVER_MODE", "dev")
COLLECTOR_HOST = os.getenv("COLLECTOR_HOST")
COLLECTOR_WEBHOOK_SECRET = os.getenv("MONOBANK_WEBHOOK_SECRET")

# SMTP stuff
SMTP_HOST = "smtp.gmail.com"
SMTP_LOGIN = os.environ["SMTP_LOGIN"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

# JWT Stuff
ACCESS_JWT_EXP_DAYS = int(os.getenv("ACCESS_JWT_EXP_DAYS", "7"))
REFRESH_JWT_EXP_DAYS = int(os.getenv("REFRESH_JWT_EXP_DAYS", "30"))
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

# Postgres stuff
POSTGRES_DRIVER_NAME = "postgres"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "swsuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "sws")
POSTGRES_POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", 1))
POSTGRES_POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", 16))
POSTGRES_RETRY_LIMIT = int(os.getenv("POSTGRES_RETRY_LIMIT", 32))
POSTGRES_RETRY_INTERVAL = int(os.getenv("POSTGRES_RETRY_INTERVAL", 1))
POSTGRES_DSN = URL(
    drivername=POSTGRES_DRIVER_NAME,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
)

# Cache stuff
RESET_PASSWORD_EXPIRE = 60 * 60 * 24  # 24h
RESET_PASSWORD_TEMPLATE = "reset-password--{code}"
TELEGRAM_TEMPLATE = "telegram--{code}"
TELEGRAM_EXPIRE = 60 * 60  # 1h

# Telegram stuff
TELEGRAM_BOT_NAME = "SheetWithoutShitBot"
TELEGRAM_BOT_INVITATION_LINK = "https://t.me/SheetWithoutShitBot?start={code}"
