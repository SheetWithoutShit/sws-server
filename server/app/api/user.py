"""This module provides user`s views."""

from http import HTTPStatus

from aiohttp import web

from app.utils.errors import SWSDatabaseError
from app.models.user import User


user_routes = web.RouteTableDef()


@user_routes.view("/user")
class UserView(web.View):
    """Class that includes functionality to work with user data in system."""

    async def get(self):
        """Retrieve user data from database by user id."""
        try:
            user = await User.get_by_id(self.request.user_id)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        return web.json_response(
            data={"success": True, "user": user.as_dict()},
            status=HTTPStatus.OK
        )
