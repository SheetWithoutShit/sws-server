"""This module provides user`s views."""

import uuid
from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn

from app.cache import cache, TELEGRAM_CACHE_KEY, TELEGRAM_CACHE_EXPIRE
from app.models.user import User
from app.utils.response import make_response
from app.utils.errors import DatabaseError
from app.utils.monobank import setup_webhook, save_user_monobank_info, save_monobank_month_transactions


user_routes = web.RouteTableDef()


@user_routes.view("/v1/user")
class UserView(web.View):
    """Class that includes functionality to work with user data in system."""

    async def get(self):
        """Retrieve user data from database by user id."""
        try:
            user = await User.get_by_id(self.request.user_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            data=user.as_dict(),
            http_status=HTTPStatus.OK,
        )

    async def delete(self):
        """Delete user and his data from system."""
        try:
            await User.delete(self.request.user_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="The user was deleted successfully.",
            http_status=HTTPStatus.OK,
        )


@user_routes.view("/v1/user/telegram")
class UserTelegramView(web.View):
    """Class that includes functionality to work with user telegram chat."""

    async def get(self):
        """Return invitation link for user to telegram bot."""
        config = self.request.app.config

        telegram_cache_code = str(uuid.uuid4())
        telegram_cache_key = TELEGRAM_CACHE_KEY.format(code=telegram_cache_code)
        await cache.set(telegram_cache_key, self.request.user_id, TELEGRAM_CACHE_EXPIRE)

        telegram_invitation_link = config.TELEGRAM_BOT_INVITATION_LINK.format(code=telegram_cache_code)
        response_data = {"invitation_link": telegram_invitation_link}
        return make_response(
            success=True,
            message="The invitation link to telegram bot was created.",
            data=response_data,
            http_status=HTTPStatus.OK,
        )


@user_routes.view("/v1/user/monobank")
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
            return make_response(
                success=False,
                message="Required field token is not provided.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        _, status = await setup_webhook(
            user_id,
            user_monobank_token,
            config.COLLECTOR_WEBHOOK_SECRET,
            config.COLLECTOR_HOST
        )
        if status != 200:
            return make_response(
                success=False,
                message="The provided token is not correct.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        await spawn(self.request, save_user_monobank_info(user_id, user_monobank_token))
        await spawn(self.request, save_monobank_month_transactions(user_id, user_monobank_token))

        return make_response(
            success=True,
            message="The monobank token was successfully applied.",
            http_status=HTTPStatus.OK,
        )


@user_routes.view("/v1/user/notifications")
class UserNotificationsView(web.View):
    """Class that includes functionality to work with user notifications."""

    async def put(self):
        """Disabled/enable user`s notifications."""
        body = self.request.body
        user_id = self.request.user_id

        try:
            notifications_enabled = body["enabled"]
        except KeyError:
            return make_response(
                success=False,
                message="Required field enabled is not provided.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        if not isinstance(notifications_enabled, bool):
            return make_response(
                success=False,
                message="The provided field enabled is not correct. Expected bool type.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            await User.update(user_id, notifications_enabled=notifications_enabled)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        result = "enabled" if notifications_enabled else "disabled"
        return make_response(
            success=True,
            message=f"The notifications were successfully {result}.",
            http_status=HTTPStatus.OK,
        )
