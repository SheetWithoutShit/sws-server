"""This module provides middlewares for server application."""

import json

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
            data={"success": False, "message": "You aren't authorized. Please provide authorization token."},
            status=401
        )

    try:
        payload = jwt.decode(token, secret, algorithm=jwt_algorithm)
    except jwt.DecodeError:
        return web.json_response(
            data={"success": False, "message": "Wrong credentials. Your token is invalid."},
            status=401
        )
    except jwt.ExpiredSignatureError:
        return web.json_response(
            data={"success": False, "message": "Wrong credentials. Your token is expired."},
            status=401
        )

    request.user_id = payload["user_id"]
    return await handler(request)


@web.middleware
async def body_validator_middleware(request, handler):
    """Check if provided body data for mutation methods is correct."""
    if request.body_exists:
        content = await request.read()
        try:
            request.body = json.loads(content)
        except json.decoder.JSONDecodeError:
            return web.json_response(
                data={"success": False, "message": "Wrong input. Can't deserialize body input."},
                status=400
            )

    return await handler(request)
