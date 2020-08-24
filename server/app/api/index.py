"""This module provides basic server endpoints."""

from http import HTTPStatus

from aiohttp import web


internal_routes = web.RouteTableDef()


@internal_routes.get("/health")
async def health_view(request):
    """Return health OK http status."""
    return web.json_response(
        data={
            "success": True,
            "message": "OK",
            "url": str(request.url)
        },
        status=HTTPStatus.OK
    )


async def handle_404(request):
    """Return custom response for 404 http status code."""
    return web.json_response(
        data={
            "success": False,
            "message": "The URL you are trying to access could not be found on the server.",
            "path": request.path
        },
        status=HTTPStatus.NOT_FOUND
    )


async def handle_405(request):
    """Return custom response for 405 http status code."""
    return web.json_response(
        data={
            "success": False,
            "message": "The method you are trying to use for this URL could not be handled on the server.",
            "method": request.method
        },
        status=HTTPStatus.METHOD_NOT_ALLOWED
    )


async def handle_500(request):
    """Return custom response for 500 http status code."""
    return web.json_response(
        data={
            "success": False,
            "message": "Something has gone wrong on the server side. Please, try again later.",
            "url": str(request.url)
        },
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
