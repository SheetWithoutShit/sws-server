"""This module provides budget views."""

from datetime import datetime, timedelta

from aiohttp import web

from app.utils.time import DATE_FORMAT, generate_days_period


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


@budget_routes.view("/budget/daily")
class BudgetWeekView(web.View):
    """Views to interact with user daily budget report."""

    async def get(self):
        """Retrieve daily budgets reports for provided user."""
        try:
            start_date = datetime.fromtimestamp(self.request.query["start_ts"])
            end_date = datetime.fromtimestamp(self.request.query["end_ts"])
        except KeyError:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        except TypeError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Query arguments start_ts or end_ts is not correct."
                },
                status=400
            )

        budget = self.request.app["budget"]
        daily_budgets = await budget.get_daily_budgets(self.request.user_id, start_date, end_date)
        if daily_budgets is None:
            return web.json_response(
                data={"success": False, "message": "Couldn't retrieve user`s daily budgets."},
                status=400
            )

        daily_budgets_map = {budget["date"]: budget["amount"] for budget in daily_budgets}
        response = [{
            "date": day.strftime(DATE_FORMAT),
            "amount": daily_budgets_map.get(day, "0")
        } for day in generate_days_period(start_date, end_date)]

        return web.json_response(
            data={"success": True, "daily_budgets": response},
            status=200
        )
