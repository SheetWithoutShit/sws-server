"""This module provides config variables for server app."""

import os


# Server stuff
APP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(APP_DIR, os.pardir))
TEMPLATES_DIR = os.path.join(APP_DIR, "templates")
SERVER_SECRET = os.environ["SERVER_SECRET"]
SERVER_MODE = os.getenv("SERVER_MODE", "dev")
NGROK_DOMAIN = None

# SMTP stuff
SMTP_HOST = "smtp.gmail.com"
SMTP_LOGIN = os.environ["SMTP_LOGIN"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

# JWT Stuff
ACCESS_JWT_EXP_DAYS = int(os.getenv("ACCESS_JWT_EXP_DAYS", "7"))
REFRESH_JWT_EXP_DAYS = int(os.getenv("REFRESH_JWT_EXP_DAYS", "30"))

# Postgres stuff
POSTGRES_DSN = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    user=os.getenv("POSTGRES_USER", "swsuser"),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    database=os.getenv("POSTGRES_DB", "sws"),
)

# Cache stuff
RESET_PASSWORD_EXPIRE = 60 * 60 * 24  # 24h
RESET_PASSWORD_TEMPLATE = "reset-password--{code}"
TELEGRAM_TEMPLATE = "telegram--{code}"
TELEGRAM_EXPIRE = 60 * 60  # 1h

# Telegram stuff
TELEGRAM_BOT_NAME = "SheetWithoutShitBot"
TELEGRAM_BOT_INVITATION_LINK = "https://t.me/SheetWithoutShitBot?start={code}"
