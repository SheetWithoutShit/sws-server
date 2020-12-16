"""This module provides transactions views."""

from http import HTTPStatus
from datetime import datetime, timedelta

from aiohttp import web

from app.models.transaction import Transaction
from app.utils.response import make_response
from app.utils.errors import DatabaseError
from app.utils.time import DATETIME_FORMAT, DATE_FORMAT, generate_days_period


transaction_routes = web.RouteTableDef()


@transaction_routes.view("/v1/transactions")
class TransactionsView(web.View):
    """Views to interact with user`s transactions."""

    async def get(self):
        """Retrieve user`s transactions for provided period."""
        try:
            start_date = datetime.strptime(self.request.query["start_date"], DATETIME_FORMAT)
            end_date = datetime.strptime(self.request.query["end_date"], DATETIME_FORMAT)
        except KeyError:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        except (TypeError, ValueError):
            return make_response(
                success=False,
                message="Query arguments start_date or end_date is not correct. "
                        f"Expected strings: {DATETIME_FORMAT}.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        category = self.request.query.get("category")
        try:
            result = await Transaction.get_transactions(self.request.user_id, category, start_date, end_date)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            data=result,
            http_status=HTTPStatus.OK,
        )


@transaction_routes.view("/v1/transactions/report/month")
class TransactionMonthReportView(web.View):
    """Views to interact with month transaction report."""

    async def get(self):
        """Retrieve month transaction report for provided user and month."""
        try:
            year = int(self.request.query["year"])
            month = int(self.request.query["month"])
        except KeyError:
            today = datetime.today()
            year, month = today.year, today.month
        except (TypeError, ValueError):
            return make_response(
                success=False,
                message="Required query arguments year or month is not correct.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            categories_reports = await Transaction.get_month_report(self.request.user_id, year, month)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        response_data = {
            "categories": categories_reports,
            "year": year,
            "month": month
        }
        return make_response(
            success=True,
            data=response_data,
            http_status=HTTPStatus.OK,
        )


@transaction_routes.view("/v1/transactions/report/daily")
class TransactionDailyReportView(web.View):
    """Views to interact with daily transaction reports."""

    async def get(self):
        """Retrieve daily transactions reports for provided user and period."""
        try:
            start_date = datetime.strptime(self.request.query["start_date"], DATETIME_FORMAT)
            end_date = datetime.strptime(self.request.query["end_date"], DATETIME_FORMAT)
        except KeyError:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
        except (TypeError, ValueError):
            return make_response(
                success=False,
                message="Query arguments start_date or end_date is not correct.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            daily_reports = await Transaction.get_daily_reports(self.request.user_id, start_date, end_date)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        daily_budgets_map = {budget["date"]: budget["amount"] for budget in daily_reports}
        response_data = [{
            "date": day.strftime(DATE_FORMAT),
            "amount": daily_budgets_map.get(day, "0")
        } for day in generate_days_period(start_date, end_date)]

        return make_response(
            success=True,
            data=response_data,
            http_status=HTTPStatus.OK,
        )
