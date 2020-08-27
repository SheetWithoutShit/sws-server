"""This module provides config variables for server app."""

import os


ACCESS_JWT_EXP_DAYS = int(os.getenv("ACCESS_JWT_EXP_DAYS", "7"))
REFRESH_JWT_EXP_DAYS = int(os.getenv("REFRESH_JWT_EXP_DAYS", "30"))
SERVER_SECRET = os.getenv("SERVER_SECRET")
POSTGRES_DSN = "postgresql://{user}:{password}@{host}:{port}/{database}".format(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    user=os.getenv("POSTGRES_USER", "swsuser"),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    database=os.getenv("POSTGRES_DB", "sws"),
)
