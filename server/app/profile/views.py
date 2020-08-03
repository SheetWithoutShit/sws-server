"""This module provides user`s profile views."""

from datetime import datetime

from aiohttp import web

from app.validators import validate_budget


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

        user_profile = self.request.app["user_profile"]
        user_budget = await user_profile.get_profile_budget(self.request.user_id, year, month)
        if not user_budget:
            return web.json_response(
                data={"success": False, "message": "Couldn't retrieve user`s budget."},
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

        errors = validate_budget(body)
        if errors:
            return web.json_response(
                data={
                    "success": False,
                    "message": f"Wrong input: {' '.join(errors)}"
                },
                status=400
            )

        user_profile = self.request.app["user_profile"]
        updated = await user_profile.update_profile_budget(self.request.user_id, year, month, body)
        if not updated:
            return web.json_response(
                data={"success": False, "message": "Couldn't update user`s budget."},
                status=400
            )

        return web.json_response(
            data={"success": True, "message": "The user`s budget was updated."},
            status=200
        )
