"""This module provides user`s views."""

import uuid
from http import HTTPStatus

from aiohttp import web

from app.models.user import User
from app.utils.errors import SWSDatabaseError


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


@user_routes.view("/user/telegram")
class UserView(web.View):
    """Class that includes functionality to work with user telegram chat."""

    async def get(self):
        """Return invitation link for user to telegram bot."""
        redis = self.request.app["redis"]
        config = self.request.app.config

        telegram_cache_code = str(uuid.uuid4())
        telegram_cache_key = config.TELEGRAM_TEMPLATE.format(code=telegram_cache_code)
        await redis.set(telegram_cache_key, self.request.user_id, config.TELEGRAM_EXPIRE)

        telegram_invitation_link = config.TELEGRAM_BOT_INVITATION_LINK.format(code=telegram_cache_code)
        return web.json_response(
            data={"success": True, "invitation_link": telegram_invitation_link},
            status=HTTPStatus.OK
        )
