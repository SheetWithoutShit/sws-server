"""This module provides auth views."""

from http import HTTPStatus

from aiohttp import web

from app.utils.errors import SWSDatabaseError
from app.utils.validators import validate_email, validate_password
from app.utils.jwt import generate_token, decode_token
from app.utils.errors import SWSTokenError
from app.models.user import User


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
