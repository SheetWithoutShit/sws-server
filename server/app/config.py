"""This module provides config variables for server app."""

import os

from sqlalchemy.engine.url import URL


# Server stuff
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
EMAILS_DIR = os.path.join(TEMPLATES_DIR, "emails")
SERVER_MODE = os.getenv("SERVER_MODE", "DEV")
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
COLLECTOR_HOST = os.getenv("COLLECTOR_HOST")
COLLECTOR_WEBHOOK_SECRET = os.getenv("MONOBANK_WEBHOOK_SECRET")

# SMTP stuff
SMTP_HOST = "smtp.gmail.com"
SMTP_LOGIN = os.getenv("SMTP_LOGIN")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# JWT Stuff
ACCESS_JWT_EXP_DAYS = int(os.getenv("ACCESS_JWT_EXP_DAYS", "7"))
REFRESH_JWT_EXP_DAYS = int(os.getenv("REFRESH_JWT_EXP_DAYS", "30"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hereisasecret")

# Postgres stuff
POSTGRES_DRIVER_NAME = "postgres"
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "spentlessuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "spentless")
POSTGRES_POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", "1"))
POSTGRES_POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", "16"))
POSTGRES_RETRY_LIMIT = int(os.getenv("POSTGRES_RETRY_LIMIT", "32"))
POSTGRES_RETRY_INTERVAL = int(os.getenv("POSTGRES_RETRY_INTERVAL", "1"))
POSTGRES_DSN_STAGING = os.getenv("DATABASE_URL")
POSTGRES_DSN_DEV = URL(
    drivername=POSTGRES_DRIVER_NAME,
    username=POSTGRES_USER,
    password=POSTGRES_PASSWORD,
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    database=POSTGRES_DB,
)

# REDIS stuff
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Telegram stuff
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_BOT_NAME = "SpentlessBot"
TELEGRAM_BOT_WEBHOOK_PATH = "/v1/telegram_webhook"
TELEGRAM_BOT_WEBHOOK_URL = f"https://{SERVER_HOST}{TELEGRAM_BOT_WEBHOOK_PATH}"
TELEGRAM_BOT_INVITATION_LINK = "https://t.me/SpentlessBot?start={code}"
