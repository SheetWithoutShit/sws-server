"""This module provides helper functionality with JWT."""

from datetime import datetime

import jwt

from app.utils.errors import TokenError


def generate_token(secret_key, private_claims=None, exp_days=None):
    """Return encoded json web token."""
    token_exp = None
    now = int(datetime.now().timestamp())
    payload = {"iat": now}

    if exp_days is not None:
        token_exp = now + (exp_days * 60 * 60 * 24)
        payload.update({"exp": token_exp})

    if private_claims:
        payload.update(private_claims)

    token = jwt.encode(payload, secret_key).decode("UTF-8")
    return token, token_exp


def decode_token(token, secret_key):
    """Return decoded payload from json web token."""
    try:
        return jwt.decode(token, secret_key)
    except jwt.DecodeError:
        raise TokenError("The token is invalid.")
    except jwt.ExpiredSignatureError:
        raise TokenError("The token has expired.")
