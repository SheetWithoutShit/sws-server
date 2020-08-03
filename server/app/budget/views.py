"""This module provides budget views."""

from datetime import datetime

from aiohttp import web


budget_routes = web.RouteTableDef()


@budget_routes.view("/budget/month")
class BudgetMonthView(web.View):
    """Views to interact with user month budget report."""

    async def get(self):
        """Retrieve month budget report for provided user."""
        try:
            year = int(self.request.query["year"])
            month = int(self.request.query["month"])
        except KeyError:
            today = datetime.today()
            year, month = today.year, today.month
        except (TypeError, ValueError):
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required arguments year or month is not correct."
                },
                status=400
            )

        budget = self.request.app["budget"]
        month_budget = await budget.get_month_budget(self.request.user_id, year, month)
        if month_budget is None:
            return web.json_response(
                data={"success": False, "message": "Couldn't retrieve user`s month budget."},
                status=400
            )

        return web.json_response(
            data={"success": True, "month_budget": month_budget, "year": year, "month": month},
            status=200
        )
