"""This module provides user`s views."""

from http import HTTPStatus

from aiohttp import web

from app.utils.validators import validate_password
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


@user_routes.view("/user/password")
class UserPasswordView(web.View):
    """Class that includes functionality to work with user password in system."""

    async def put(self):
        """Change password for user in case provided old password is correct."""
        body = self.request.body
        try:
            old_password, new_password = body["old_password"], body["new_password"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required fields old_password or new_password is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            user = await User.get_by_id(self.request.user_id)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        is_correct = user.check_password_hash(old_password)
        if not is_correct:
            return web.json_response(
                data={
                    "success": False,
                    "message": "The provided old password is not correct."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        validation_errors = validate_password(new_password)
        if validation_errors:
            return web.json_response(
                data={"success": False, "message": f"Invalid new password: {' '.join(validation_errors)}"},
                status=HTTPStatus.BAD_REQUEST
            )

        password_hash = User.generate_password_hash(new_password)
        try:
            await User.update_user(self.request.user_id, password=password_hash)
        except SWSDatabaseError:
            return web.json_response(
                data={"success": False, "message": "Failed to update user password."},
                status=HTTPStatus.BAD_REQUEST
            )

        return web.json_response(
            data={"success": True, "message": "The password was changed successfully."},
            status=HTTPStatus.OK
        )
