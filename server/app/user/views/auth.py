"""This module provides user`s auth views."""

from aiohttp import web

from app.utils.jwt import generate_auth_token
from app.validators import validate_email, validate_password


auth_views = web.RouteTableDef()


@auth_views.view("/user/signup")
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
                status=400
            )

        validation_errors = validate_password(password) + validate_email(email)
        if validation_errors:
            return web.json_response(
                data={"success": False, "message": f"Wrong input: {' '.join(validation_errors)}"},
                status=400
            )

        user = self.request.app["user"]
        result = await user.create_user(email, password)
        if isinstance(result, str):
            return web.json_response(
                data={"success": False, "message": result},
                status=400
            )

        secret_key = self.request.app["constants"]["SERVER_SECRET"]
        jwt_exp_days = self.request.app["constants"]["JWT_EXP_DAYS"]
        token = generate_auth_token(result["id"], secret_key, jwt_exp_days)
        return web.json_response(
            data={"success": True, **token},
            status=200
        )


@auth_views.view("/user/signin")
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
                status=400
            )

        user = self.request.app["user"]
        result = await user.get_user_by_email(email)
        if isinstance(result, str):
            return web.json_response(
                data={"success": False, "message": result},
                status=401
            )

        is_correct = user.check_password_hash(result["password"], password)
        if not is_correct:
            return web.json_response(
                data={
                    "success": False,
                    "message": f"The provided password for user {email} is not correct."
                },
                status=401
            )


        secret_key = self.request.app["constants"]["SERVER_SECRET"]
        jwt_exp_days = self.request.app["constants"]["JWT_EXP_DAYS"]
        token = generate_auth_token(result["id"], secret_key, jwt_exp_days)
        return web.json_response(
            data={"success": True, **token},
            status=200
        )
