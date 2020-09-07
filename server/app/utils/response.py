"""This module provides helper functionality for web responses."""

from aiohttp import web


def make_response(success, http_status, data=None, message=None):
    """Return formatted json response."""
    response = {
        "success": success,
        "message": message,
        "data": data
    }
    return web.json_response(response, status=http_status)
