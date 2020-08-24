"""This module provides middlewares for server application."""

import json

from aiohttp import web

from app.utils.errors import SWSTokenError
from app.utils.jwt import decode_auth_token


SAFE_ROUTES = [
    "/health",
    "/user/signup",
    "/user/signin"
]


def error_middleware(error_handlers):
    """Return custom error handler."""

    @web.middleware
    async def error_middleware_inner(request, handler):
        """Handle specific http errors using custom views."""
        try:
            return await handler(request)
        except web.HTTPException as ex:
            error_handler = error_handlers.get(ex.status)
            if error_handler:
                return await error_handler(request)

            raise ex

    return error_middleware_inner


@web.middleware
async def auth_middleware(request, handler):
    """Check if authorization token in headers is correct."""
    if any([route == request.path for route in SAFE_ROUTES]):
        return await handler(request)

    token = request.headers.get("Authorization")
    if not token:
        return web.json_response(
            data={"success": False, "message": "You aren't authorized. Please provide authorization token."},
            status=401
        )

    secret_key = request.app.config.SERVER_SECRET
    try:
        payload = decode_auth_token(token, secret_key)
    except SWSTokenError as err:
        return web.json_response(
            data={"success": False, "message": f"Wrong credentials. {str(err)}"},
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
