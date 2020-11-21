"""This module provides budget views."""

from http import HTTPStatus

from aiohttp import web

from app.models.budget import Budget
from app.utils.response import make_response
from app.utils.errors import DatabaseError
from app.utils.validators import validate_budget_savings, validate_budget_income


budget_routes = web.RouteTableDef()


@budget_routes.view("/v1/budget")
class UserProfileBudgetView(web.View):
    """Views to interact with user`s profile budget data."""

    async def get(self):
        """Retrieve user`s profile budget information."""
        try:
            budget = await Budget.get_budget(self.request.user_id)
        except DatabaseError as err:
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

        income, savings = body.get("income"), body.get("savings")
        validation_errors = validate_budget_income(income) + validate_budget_savings(savings)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Wrong input: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            await Budget.update_budget(self.request.user_id, savings, income)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="Success. The user`s budget was updated.",
            http_status=HTTPStatus.OK
        )
