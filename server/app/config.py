"""This module provides config variables for server app."""

import os


SMTP_HOST = "smtp.gmail.com"
SMTP_LOGIN = os.environ["SMTP_LOGIN"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]

ACCESS_JWT_EXP_DAYS = int(os.getenv("ACCESS_JWT_EXP_DAYS", "7"))
REFRESH_JWT_EXP_DAYS = int(os.getenv("REFRESH_JWT_EXP_DAYS", "30"))

SERVER_SECRET = os.environ["SERVER_SECRET"]

POSTGRES_DSN = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    user=os.getenv("POSTGRES_USER", "swsuser"),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    database=os.getenv("POSTGRES_DB", "sws"),
)
