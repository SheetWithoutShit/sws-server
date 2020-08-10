"""This module provides user`s user views."""

from datetime import datetime

from aiohttp import web

from app.errors import SWSDatabaseError
from app.validators import validate_budget_income, validate_budget_savings


profile_routes = web.RouteTableDef()


@profile_routes.view("/user/profile/budget")
class UserProfileBudgetView(web.View):
    """Views to interact with user`s profile budget data."""

    async def get(self):
        """Retrieve user`s profile budget information."""
        today = datetime.today()
        try:
            year = int(self.request.query.get("year", today.year))
            month = int(self.request.query.get("month", today.month))
        except (TypeError, ValueError):
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Query arguments year or month is not correct"
                },
                status=400
            )

        user = self.request.app["user"]
        try:
            user_budget = await user.get_profile_budget(self.request.user_id, year, month)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=400
            )

        return web.json_response(
            data={"success": True, "budget": user_budget},
            status=200
        )

    async def put(self):
        """Update user`s profile budget information."""
        body = self.request.body
        try:
            year, month = int(body["year"]), int(body["month"])
        except (KeyError, TypeError, ValueError):
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required fields year or month is not correct."
                },
                status=400
            )

        income, savings = body.get("income"), body.get("savings")
        validation_errors = []
        if income is not None:
            validation_errors.extend(validate_budget_income(income))
        if savings is not None:
            validation_errors.extend(validate_budget_savings(savings))
        if validation_errors:
            return web.json_response(
                data={
                    "success": False,
                    "message": f"Wrong input: {' '.join(validation_errors)}"
                },
                status=400
            )

        user = self.request.app["user"]
        try:
            await user.update_profile_budget(self.request.user_id, year, month, body)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=400
            )

        return web.json_response(
            data={"success": True, "message": "The user`s budget was updated."},
            status=200
        )
