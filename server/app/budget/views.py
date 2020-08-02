"""This module provides budget views."""

from aiohttp import web


budget_routes = web.RouteTableDef()


@budget_routes.view(r"/user/{user_id:\d+}/budget")
class BudgetView(web.View):
    """Views to interact with user`s budget data."""

    async def get(self):
        """Retrieve user`s budget information."""
        # TODO: just for test purposes
        return web.json_response(
            data={"success": True, "user_id": self.request.user_id},
            status=200
        )
