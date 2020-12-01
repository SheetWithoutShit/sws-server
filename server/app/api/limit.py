"""This module provides limit views."""

from http import HTTPStatus
from datetime import datetime

from aiohttp import web

from app.models.limit import Limit
from app.models.mcc import MCCCategory
from app.models.transaction import Transaction
from app.utils.response import make_response
from app.utils.errors import DatabaseError
from app.utils.validators import validate_limit_amount


limit_routes = web.RouteTableDef()


@limit_routes.view("/v1/limits/categories")
class BudgetLimitCategoriesView(web.View):
    """Views to interact with limit categories."""

    async def get(self):
        """Retrieve all existing categories for limits."""
        try:
            categories = await MCCCategory.get_names()
        except DatabaseError as err:
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


@limit_routes.view("/v1/limits")
class BudgetLimitsView(web.View):
    """Views to interact with budget limits."""

    async def get(self):
        """Retrieve user`s budget limits."""
        today = datetime.today()
        year, month = today.year, today.month

        try:
            limits = await Limit.get_user_limits(self.request.user_id)
            spendings = await Transaction.get_month_report(self.request.user_id, year, month)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        # set spent amount for each limit
        for limit in limits:
            spending = next((item for item in spendings if item["name"] == limit["name"]), {})
            limit["spent"] = spending.get("amount", "0.0")

        return make_response(
            success=True,
            data=limits,
            http_status=HTTPStatus.OK
        )

    async def post(self):
        """Create a new budget limit for user."""
        body = self.request.body

        try:
            category_name, amount = body["category"], body["amount"]
        except KeyError:
            return make_response(
                success=False,
                message="Wrong input. Required fields category or amount is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            category = await MCCCategory.get_by_name(category_name)
        except DatabaseError as err:
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
            limit = await Limit.create(self.request.user_id, category.id, amount)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        response_data = {"category": category_name, **limit.as_dict()}
        return make_response(
            success=True,
            message="Success. The budget limit for user was created.",
            data=response_data,
            http_status=HTTPStatus.OK
        )


@limit_routes.view(r"/v1/limits/{limit_id:\d+}")
class LimitView(web.View):
    """Views to interact with user's budget limit."""

    async def put(self):
        """Update user's budget limit."""
        body = self.request.body

        try:
            amount = body["amount"]
        except KeyError:
            return make_response(
                success=False,
                message="Wrong input. Required field amount is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        validation_errors = validate_limit_amount(amount)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Wrong input: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        limit_id = int(self.request.match_info["limit_id"])
        try:
            limit = await Limit.get_by_id(limit_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        if limit.user_id != self.request.user_id:
            return make_response(
                success=False,
                message="Forbidden. You don't have permission to edit this limit.",
                http_status=HTTPStatus.FORBIDDEN
            )

        try:
            await Limit.update(limit.id, amount)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="Success. The user`s budget limit was updated.",
            http_status=HTTPStatus.OK
        )

    async def delete(self):
        """Delete user's budget limit."""
        limit_id = int(self.request.match_info["limit_id"])
        try:
            await Limit.delete(limit_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="Success. The user`s budget limit was deleted.",
            http_status=HTTPStatus.OK
        )
