"""This module provides basic server endpoints."""

from http import HTTPStatus

from aiohttp import web

from app.utils.response import make_response


internal_routes = web.RouteTableDef()


@internal_routes.get("/health")
async def health_view(request):
    """Return health OK http status."""
    return make_response(
        success=True,
        message=f"OK. URL: {str(request.url)}",
        http_status=HTTPStatus.OK
    )


async def handle_404(request):
    """Return custom response for 404 http status code."""
    return make_response(
        success=False,
        message=f"The endpoint ({request.path}) you are trying to access could not be found on the server.",
        http_status=HTTPStatus.NOT_FOUND
    )


async def handle_405(request):
    """Return custom response for 405 http status code."""
    return make_response(
        success=False,
        message=f"The method ({request.method}) you are trying to use for this URL could not be handled on the server.",
        http_status=HTTPStatus.METHOD_NOT_ALLOWED
    )


async def handle_500(request):
    """Return custom response for 500 http status code."""
    return make_response(
        success=False,
        message=f"Something has gone wrong on the server side (URL - {str(request.url)}). Please, try again later.",
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
