"""This module provides helper functionality with JWT."""

from datetime import datetime, timedelta

import jwt

from app.utils.errors import SWSTokenError
from app.utils.time import DATETIME_FORMAT


def generate_auth_token(user_id, secret_key, exp_days=7):
    """Return encoded token for user authorization"""
    now = datetime.now()
    exp = now + timedelta(days=exp_days)
    payload = {
        "exp": exp,
        "iat": now,
        "user_id": user_id
    }
    token = jwt.encode(payload, secret_key)

    return {
        "token": token.decode("utf-8"),
        "token_exp": exp.strftime(DATETIME_FORMAT)
    }


def decode_auth_token(token, secret_key):
    """Return decoded payload from authorization token."""
    try:
        return jwt.decode(token, secret_key)
    except jwt.DecodeError:
        raise SWSTokenError("The token is invalid.")
    except jwt.ExpiredSignatureError:
        raise SWSTokenError("The token has expired.")
