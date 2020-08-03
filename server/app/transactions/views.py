"""This module provides transactions views."""

from datetime import datetime

from aiohttp import web


transaction_routes = web.RouteTableDef()


@transaction_routes.view("/transactions")
class TransactionsView(web.View):
    """Views to interact with user`s transactions."""

    async def get(self):
        """Retrieve user`s transactions for provided period."""
        now = datetime.now().timestamp()
        start_ts = self.request.query.get("start_ts", now - 86400)  # 1 day in seconds
        end_ts = self.request.query.get("end_ts", now)
        try:
            start_date = datetime.fromtimestamp(start_ts)
            end_date = datetime.fromtimestamp(end_ts)
        except TypeError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Query arguments start_ts or end_ts is not correct."
                },
                status=400
            )

        transaction = self.request.app["transaction"]
        transactions = await transaction.get_transactions(self.request.user_id, start_date, end_date)
        if transactions is None:
            return web.json_response(
                data={"success": False, "message": "Couldn't retrieve user`s transactions."},
                status=400
            )

        return web.json_response(
            data={"success": True, "transactions": transactions},
            status=200
        )
