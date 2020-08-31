"""This module provides auth views."""

import uuid
from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn
from aiohttp_jinja2 import render_template

from app.models.user import User
from app.utils.errors import SWSDatabaseError
from app.utils.validators import validate_email, validate_password
from app.utils.jwt import generate_token, decode_token
from app.utils.errors import SWSTokenError
from app.utils.mail import send_reset_password_mail
from app.config import RESET_PASSWORD_EXPIRE, RESET_PASSWORD_TEMPLATE


auth_routes = web.RouteTableDef()


@auth_routes.view("/auth/signup")
class AuthSignUp(web.View):
    """Class that includes functionality to sign up user in system."""

    async def post(self):
        """Create a new user in system."""
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

        password_hash = User.generate_password_hash(password)
        try:
            user = await User.create_user(email=email, password=password_hash)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        return web.json_response(
            data={
                "success": True,
                "message": f"The user was created successfully: {user.email}."
            },
            status=HTTPStatus.OK
        )


@auth_routes.view("/auth/signin")
class AuthSignIn(web.View):
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

        secret = self.request.app.config.SERVER_SECRET
        token, token_exp = generate_token(
            secret_key=secret,
            private_claims={"user_id": user.id},
            exp_days=self.request.app.config.ACCESS_JWT_EXP_DAYS
        )
        refresh_token, refresh_token_exp = generate_token(
            secret_key=secret,
            private_claims={"user_id": user.id},
            exp_days=self.request.app.config.REFRESH_JWT_EXP_DAYS
        )
        return web.json_response(
            data={
                "success": True,
                "access_token": token, "access_token_exp": token_exp,
                "refresh_access_token": refresh_token, "refresh_access_token_exp": refresh_token_exp
            },
            status=HTTPStatus.OK
        )


@auth_routes.view("/auth/refresh_access")
class AuthRefreshAccess(web.View):
    """Class that includes functionality to refresh access token for user."""

    async def post(self):
        """Return refreshed access token for a user."""
        body = self.request.body
        try:
            refresh_token = body["refresh_access_token"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required field refresh_access_token is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        secret_key = self.request.app.config.SERVER_SECRET
        try:
            payload = decode_token(refresh_token, secret_key)
        except SWSTokenError as err:
            return web.json_response(
                data={"success": False, "message": f"Wrong refresh access token. {str(err)}"},
                status=HTTPStatus.BAD_REQUEST
            )

        user_id = payload["user_id"]
        token, token_exp = generate_token(
            secret_key=secret_key,
            private_claims={"user_id": user_id},
            exp_days=self.request.app.config.ACCESS_JWT_EXP_DAYS
        )
        refresh_token, refresh_token_exp = generate_token(
            secret_key=secret_key,
            private_claims={"user_id": user_id},
            exp_days=self.request.app.config.REFRESH_JWT_EXP_DAYS
        )
        return web.json_response(
            data={
                "success": True,
                "access_token": token, "access_token_exp": token_exp,
                "refresh_access_token": refresh_token, "refresh_access_token_exp": refresh_token_exp
            },
            status=HTTPStatus.OK
        )


@auth_routes.view("/auth/change_password")
class AuthChangePasswordView(web.View):
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


@auth_routes.view("/auth/reset_password")
class AuthResetPasswordView(web.View):
    """Class that includes functionality to kick off user password resetting."""

    async def get(self):
        """Render reset password form."""
        try:
            reset_password_code = self.request.query["reset_password_code"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required param code is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        return render_template(
            "reset_password.html",
            self.request,
            {"reset_password_code": reset_password_code}
        )

    async def post(self):
        """Kick off user password resetting."""
        body = self.request.body
        redis = self.request.app["redis"]

        try:
            email = body["email"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required field email is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        try:
            user = await User.get_by_email(email)
        except SWSDatabaseError as err:
            return web.json_response(
                data={"success": False, "message": str(err)},
                status=HTTPStatus.BAD_REQUEST
            )

        reset_password_code = str(uuid.uuid4())
        reset_password_key = RESET_PASSWORD_TEMPLATE.format(code=reset_password_code)
        await redis.set(reset_password_key, user.id, RESET_PASSWORD_EXPIRE)

        reset_password_url = self.request.url.update_query({"reset_password_code": reset_password_code})
        await spawn(self.request, send_reset_password_mail(user, str(reset_password_url)))

        return web.json_response(
            data={
                "success": True,
                "message": f"The email with link for password resetting should soon be delivered to {user.email}."
            },
            status=HTTPStatus.OK
        )

    async def put(self):
        """Create a new password for user."""
        body = self.request.body
        redis = self.request.app["redis"]

        try:
            new_password = body["new_password"]
            reset_password_code = body["reset_password_code"]
        except KeyError:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required field new_password or reset_password_code is not provided."
                },
                status=HTTPStatus.BAD_REQUEST
            )

        reset_password_key = RESET_PASSWORD_TEMPLATE.format(code=reset_password_code)
        user_id = await redis.get(reset_password_key)
        if user_id is None:
            return web.json_response(
                data={
                    "success": False,
                    "message": "Wrong input. Required field reset_password_code is not correct or expired."
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
            await User.update_user(int(user_id), password=password_hash)
        except SWSDatabaseError:
            return web.json_response(
                data={"success": False, "message": "Failed to update user password."},
                status=HTTPStatus.BAD_REQUEST
            )

        await spawn(self.request, redis.remove(reset_password_key))
        return web.json_response(
            data={"success": True, "message": "The password was changed successfully."},
            status=HTTPStatus.OK
        )
