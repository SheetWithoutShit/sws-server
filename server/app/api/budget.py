"""This module provides budget views."""

from http import HTTPStatus
from datetime import datetime

from aiohttp import web

from app.models.budget import Budget
from app.utils.response import make_response
from app.utils.errors import SWSDatabaseError
from app.utils.validators import validate_budget_savings, validate_budget_income


budget_routes = web.RouteTableDef()


@budget_routes.view("/budget")
class UserProfileBudgetView(web.View):
    """Views to interact with user`s profile budget data."""

    async def get(self):
        """Retrieve user`s profile budget information."""
        today = datetime.today()
        try:
            year = int(self.request.query.get("year", today.year))
            month = int(self.request.query.get("month", today.month))
        except (TypeError, ValueError):
            return make_response(
                success=False,
                message="Wrong input. Query arguments year or month is not correct",
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            budget = await Budget.get_budget(self.request.user_id, year, month)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            data=budget.as_dict(),
            http_status=HTTPStatus.OK
        )

    async def put(self):
        """Update user`s profile budget information."""
        body = self.request.body
        try:
            year, month = int(body["year"]), int(body["month"])
        except (KeyError, TypeError, ValueError):
            return make_response(
                success=False,
                message="Wrong input. Required fields year or month is not correct.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        income, savings = body.get("income"), body.get("savings")
        validation_errors = validate_budget_income(income) + validate_budget_savings(savings)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Wrong input: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            await Budget.update_budget(self.request.user_id, year, month, savings, income)
        except SWSDatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="The user`s budget was updated.",
            http_status=HTTPStatus.OK
        )
