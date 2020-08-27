"""This module provides helper functionality with JWT."""

from datetime import datetime, timedelta

import jwt

from app.utils.errors import SWSTokenError
from app.utils.time import DATETIME_FORMAT


def generate_token(secret_key, private_claims=None, exp_days=7):
    """Return encoded json web token."""
    if not private_claims:
        private_claims = {}

    now = datetime.now()
    exp = now + timedelta(days=exp_days)
    payload = {
        "exp": exp,
        "iat": now,
        **private_claims
    }
    token = jwt.encode(payload, secret_key).decode("UTF-8")
    token_exp = exp.strftime(DATETIME_FORMAT)

    return token, token_exp


def decode_token(token, secret_key):
    """Return decoded payload from json web token."""
    try:
        return jwt.decode(token, secret_key)
    except jwt.DecodeError:
        raise SWSTokenError("The token is invalid.")
    except jwt.ExpiredSignatureError:
        raise SWSTokenError("The token has expired.")
