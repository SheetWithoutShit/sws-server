"""This module provides limit views."""

from http import HTTPStatus

from aiohttp import web

from app.models.limit import Limit
from app.models.mcc import MCCCategory
from app.utils.response import make_response
from app.utils.errors import SWSDatabaseError
from app.utils.validators import validate_limit_amount


limit_routes = web.RouteTableDef()


@limit_routes.view("/limits/categories")
class LimitCategoriesView(web.View):
    """Views to interact with limit categories."""

    async def get(self):
        """Retrieve all existing categories for limits."""
        try:
            categories = await MCCCategory.get_categories()
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            data=categories,
            http_status=HTTPStatus.OK
        )


@limit_routes.view("/limits")
class LimitsView(web.View):
    """Views to interact with user budget categories limits."""

    async def get(self):
        """Retrieve user`s budget categories limits."""
        try:
            limits = await Limit.get_user_limits(self.request.user_id)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            data=limits,
            http_status=HTTPStatus.OK
        )

    async def post(self):
        """Create user budget category limit."""
        body = self.request.body

        try:
            category_name, amount = body["category"], body["amount"]
        except KeyError:
            return make_response(
                success=False,
                message="Wrong input. Required fields category or amount is not provided.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            category = await MCCCategory.get_by_name(category_name)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        validation_errors = validate_limit_amount(amount)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Wrong input: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            limit = await Limit.create_limit(self.request.user_id, category.id, amount)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        response_data = {"category": category_name, **limit.as_dict()}
        return make_response(
            success=True,
            message="The user`s budget category limit was created.",
            data=response_data,
            http_status=HTTPStatus.OK
        )
