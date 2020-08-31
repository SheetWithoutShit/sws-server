"""This module provides user`s views."""

import uuid
from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn

from app.models.user import User
from app.utils.errors import SWSDatabaseError
from app.utils.monobank import setup_webhook, save_user_monobank_info, save_monobank_month_transactions


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
class UserTelegramView(web.View):
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


@user_routes.view("/user/monobank")
class UserMonobankView(web.View):
    """Class that includes functionality to work with monobank token."""

    async def put(self):
        """Update user`s monobank access token."""
        body = self.request.body
        config = self.request.app.config
        user_id = self.request.user_id

        try:
            user_monobank_token = body["token"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required field token is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        _, status = await setup_webhook(
            user_id,
            user_monobank_token,
            config.COLLECTOR_WEBHOOK_SECRET,
            config.COLLECTOR_HOST
        )
        if status != 200:
            return web.json_response(
                data={"success": False, "message": "Wrong input. Required field token is not correct."},
                status=400
            )

        await spawn(self.request, save_user_monobank_info(user_id, user_monobank_token))
        await spawn(self.request, save_monobank_month_transactions(user_id, user_monobank_token))

        return web.json_response(
            data={
                "success": True,
                "message": "The monobank token was applied successfully."
            },
            status=200
        )
