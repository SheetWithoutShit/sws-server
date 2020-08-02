"""This module provides middlewares for server application."""

import jwt

from aiohttp import web


@web.middleware
async def auth_middleware(request, handler):
    """Check if authorization token in headers is correct."""
    token = request.headers.get("Authorization")
    secret = request.app["constants"]["SERVER_SECRET"]
    jwt_algorithm = request.app["constants"]["JWT_ALGORITHM"]

    if not token:
        return web.json_response(
            data={"message": "You aren't authorized. Please provide authorization token."},
            status=401
        )

    try:
        payload = jwt.decode(token, secret, algorithm=jwt_algorithm)
    except jwt.DecodeError:
        return web.json_response(
            data={"message": "Wrong credentials. Your token is invalid."},
            status=401
        )
    except jwt.ExpiredSignatureError:
        return web.json_response(
            data={"message": "Wrong credentials. Your token is expired."},
            status=401
        )

    request.user_id = payload["user_id"]
    return await handler(request)
