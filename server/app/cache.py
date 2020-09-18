"""This module provides functionality for cache interactions."""

from aiocache import Cache

from app.config import REDIS_HOST, REDIS_PORT

MONTH_REPORT_CACHE_KEY = "month-report--{user_id}-{month}-{year}"
MONTH_REPORT_CACHE_EXPIRE = 60 * 60 * 24 * 30  # 30 days
MCC_CODES_CACHE_KEY = "mcc-codes"
CHANGE_EMAIL_CACHE_KEY = "change-email--{code}"
CHANGE_EMAIL_CACHE_EXPIRE = 60 * 60 * 24  # 48h
RESET_PASSWORD_CACHE_KEY = "reset-password--{code}"
RESET_PASSWORD_CACHE_EXPIRE = 60 * 60 * 24  # 24h
TELEGRAM_CACHE_KEY = "telegram--{code}"
TELEGRAM_CACHE_EXPIRE = 60 * 60  # 1h

cache = Cache(Cache.REDIS, endpoint=REDIS_HOST, port=REDIS_PORT)
