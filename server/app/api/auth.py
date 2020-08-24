"""This module provides user`s auth views."""

from http import HTTPStatus

from aiohttp import web

from app.utils.errors import SWSDatabaseError
from app.utils.validators import validate_email, validate_password
from app.utils.jwt import generate_auth_token
from app.models.user import User


auth_routes = web.RouteTableDef()


@auth_routes.view("/user/signup")
class UserSignUp(web.View):
    """Class that includes functionality to sign up user in system."""

    async def post(self):
        """Create a new user in system and generate auth token for him."""
        body = self.request.body
        try:
            email, password = body["email"], body["password"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required fields email or password is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        validation_errors = validate_password(password) + validate_email(email)
        if validation_errors:
            return web.json_response(
                data={"success": False, "message": f"Wrong input: {' '.join(validation_errors)}"},
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            user = await User.create(email=email, password=password)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        token = generate_auth_token(
            user.id,
            secret_key=self.request.app.config.SERVER_SECRET,
            exp_days=self.request.app.config.JWT_EXP_DAYS
        )
        return web.json_response(
            data={"success": True, **token},
            status=HTTPStatus.OK
        )


@auth_routes.view("/user/signin")
class UserSignIn(web.View):
    """Class that includes functionality to sign in user in system."""

    async def post(self):
        """Login a user if the supplied credentials are correct."""
        body = self.request.body
        try:
            email, password = body["email"], body["password"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required fields email or password is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            user = await User.get_by_email(email)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.UNAUTHORIZED
            )

        is_correct = user.check_password_hash(password)
        if not is_correct:
            return web.json_response(
                data={
                    "success": False,
                    "message": f"The provided password for user {email} is not correct."
                },
                status=HTTPStatus.UNAUTHORIZED
            )

        token = generate_auth_token(
            user.id,
            secret_key=self.request.app.config.SERVER_SECRET,
            exp_days=self.request.app.config.JWT_EXP_DAYS
        )
        return web.json_response(
            data={"success": True, **token},
            status=HTTPStatus.OK
        )
