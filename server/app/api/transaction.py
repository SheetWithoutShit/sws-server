"""This module provides transactions views."""

from http import HTTPStatus
from datetime import datetime, timedelta

from aiohttp import web

from app.utils.errors import SWSDatabaseError
from app.models.transaction import Transaction
from app.utils.time import DATETIME_FORMAT, DATE_FORMAT, generate_days_period


transaction_routes = web.RouteTableDef()


@transaction_routes.view("/transactions")
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
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Query arguments start_date or end_date is not correct. "
                               "Expected string: {DATETIME_FORMAT}."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            result = await Transaction.get_transactions(self.request.user_id, start_date, end_date)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        transactions = [transaction.as_dict() for transaction in result]
        return web.json_response(
            data={"success": True, "transactions": transactions},
            status=HTTPStatus.OK
        )


@transaction_routes.view("/transactions/report/month")
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
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required arguments year or month is not correct."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            result = await Transaction.get_month_report(self.request.user_id, year, month)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        month_report = [dict(item) for item in result]
        return web.json_response(
            data={"success": True, "report": month_report, "year": year, "month": month},
            status=HTTPStatus.OK
        )


@transaction_routes.view("/transactions/report/daily")
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
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Query arguments start_date or end_date is not correct."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            daily_reports = await Transaction.get_daily_reports(self.request.user_id, start_date, end_date)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        daily_budgets_map = {budget["date"]: budget["amount"] for budget in daily_reports}
        response = [{
            "date": day.strftime(DATE_FORMAT),
            "amount": daily_budgets_map.get(day, "0")
        } for day in generate_days_period(start_date, end_date)]

        return web.json_response(
            data={"success": True, "daily_budgets": response},
            status=HTTPStatus.OK
        )
