"""This module provides auth views."""

import uuid
from http import HTTPStatus

from aiohttp import web
from aiojobs.aiohttp import spawn
from aiohttp_jinja2 import render_template

from app.cache import (
    cache,
    RESET_PASSWORD_CACHE_KEY,
    RESET_PASSWORD_CACHE_EXPIRE,
    CHANGE_EMAIL_CACHE_KEY,
    CHANGE_EMAIL_CACHE_EXPIRE
)
from app.models.user import User
from app.utils.response import make_response
from app.utils.errors import DatabaseError
from app.utils.validators import validate_email, validate_password
from app.utils.jwt import generate_token, decode_token
from app.utils.errors import TokenError
from app.utils.mail import send_reset_password_mail, send_change_email_mail, send_user_signup_mail


auth_routes = web.RouteTableDef()


@auth_routes.view("/v1/auth/signup")
class AuthSignUp(web.View):
    """Class that includes functionality to sign up user in system."""

    async def post(self):
        """Create a new user in system."""
        body = self.request.body
        try:
            email, password = body["email"], body["password"]
        except KeyError:
            return make_response(
                success=False,
                message="Required fields email or password is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        validation_errors = validate_password(password) + validate_email(email)
        if validation_errors:
            return make_response(
                success=False,
                message=' '.join(validation_errors),
                http_status=HTTPStatus.BAD_REQUEST
            )

        password_hash = User.generate_password_hash(password)
        try:
            user = await User.create(email=email, password=password_hash)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        await spawn(self.request, send_user_signup_mail(user.email))

        response_data = {"id": user.id, "email": user.email}
        return make_response(
            success=True,
            message="The user was created.",
            data=response_data,
            http_status=HTTPStatus.CREATED,
        )


@auth_routes.view("/v1/auth/signin")
class AuthSignIn(web.View):
    """Class that includes functionality to sign in user in system."""

    async def post(self):
        """Login a user if the supplied credentials are correct."""
        body = self.request.body
        config = self.request.app.config

        try:
            email, password = body["email"], body["password"]
        except KeyError:
            return make_response(
                success=False,
                message="Required fields email or password is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            user = await User.get_by_email(email)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.UNAUTHORIZED
            )

        is_correct = user.check_password_hash(password)
        if not is_correct:
            return make_response(
                success=False,
                message=f"The provided password for user {email} is not correct.",
                http_status=HTTPStatus.UNAUTHORIZED
            )

        token, token_exp = generate_token(
            secret_key=config.JWT_SECRET_KEY,
            private_claims={"user_id": user.id},
            exp_days=config.ACCESS_JWT_EXP_DAYS
        )
        refresh_token, refresh_token_exp = generate_token(
            secret_key=config.JWT_SECRET_KEY,
            private_claims={"user_id": user.id},
            exp_days=config.REFRESH_JWT_EXP_DAYS
        )

        response_data = {
            "access_token": token, "access_token_exp": token_exp,
            "refresh_access_token": refresh_token, "refresh_access_token_exp": refresh_token_exp
        }
        return make_response(
            success=True,
            message="The user was authorized.",
            data=response_data,
            http_status=HTTPStatus.OK,
        )


@auth_routes.view("/v1/auth/refresh_access")
class AuthRefreshAccess(web.View):
    """Class that includes functionality to refresh access token for user."""

    async def post(self):
        """Return refreshed access token for a user."""
        body = self.request.body
        config = self.request.app.config

        try:
            refresh_token = body["refresh_access_token"]
        except KeyError:
            return make_response(
                success=False,
                message="Required field refresh_access_token is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            payload = decode_token(refresh_token, config.JWT_SECRET_KEY)
        except TokenError as err:
            return make_response(
                success=False,
                message=f"Invalid refresh access token. {str(err)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        user_id = payload["user_id"]
        token, token_exp = generate_token(
            secret_key=config.JWT_SECRET_KEY,
            private_claims={"user_id": user_id},
            exp_days=config.ACCESS_JWT_EXP_DAYS
        )
        refresh_token, refresh_token_exp = generate_token(
            secret_key=config.JWT_SECRET_KEY,
            private_claims={"user_id": user_id},
            exp_days=config.REFRESH_JWT_EXP_DAYS
        )

        response_data = {
            "access_token": token, "access_token_exp": token_exp,
            "refresh_access_token": refresh_token, "refresh_access_token_exp": refresh_token_exp
        }
        return make_response(
            success=True,
            message="The access token was refreshed.",
            data=response_data,
            http_status=HTTPStatus.OK,
        )


@auth_routes.view("/v1/auth/change_password")
class AuthChangePasswordView(web.View):
    """Class that includes functionality to work with user password in system."""

    async def put(self):
        """Change password for user in case provided old password is correct."""
        body = self.request.body
        try:
            old_password, new_password = body["old_password"], body["new_password"]
        except KeyError:
            return make_response(
                success=False,
                message="Required fields old_password or new_password is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            user = await User.get_by_id(self.request.user_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        is_correct = user.check_password_hash(old_password)
        if not is_correct:
            return make_response(
                success=False,
                message="The provided old password is not correct.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        validation_errors = validate_password(new_password)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Invalid new password: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        password_hash = User.generate_password_hash(new_password)
        try:
            await User.update(self.request.user_id, password=password_hash)
        except DatabaseError:
            return make_response(
                success=False,
                message="The user password was not changed.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        return make_response(
            success=True,
            message="The user password was changed.",
            http_status=HTTPStatus.OK,
        )


@auth_routes.view("/v1/auth/reset_password")
class AuthResetPasswordView(web.View):
    """Class that includes functionality for user password resetting."""

    async def get(self):
        """Render reset password form."""
        try:
            reset_password_code = self.request.query["reset_password_code"]
        except KeyError:
            return make_response(
                success=False,
                message="Required param reset_password_code is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        return render_template(
            "reset_password.html",
            self.request,
            {"reset_password_code": reset_password_code}
        )

    async def post(self):
        """Kick off user password resetting."""
        body = self.request.body

        try:
            email = body["email"]
        except KeyError:
            return make_response(
                success=False,
                message="Required field email is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        try:
            user = await User.get_by_email(email)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        reset_password_code = str(uuid.uuid4())
        reset_password_key = RESET_PASSWORD_CACHE_KEY.format(code=reset_password_code)
        await cache.set(reset_password_key, user.id, RESET_PASSWORD_CACHE_EXPIRE)

        reset_password_url = self.request.url.update_query({"reset_password_code": reset_password_code})
        await spawn(self.request, send_reset_password_mail(user, str(reset_password_url)))

        return make_response(
            success=True,
            message=f"The email with link for password resetting should soon be delivered to {user.email}.",
            http_status=HTTPStatus.OK,
        )

    async def put(self):
        """Create a new password for user."""
        body = self.request.body

        try:
            new_password = body["new_password"]
            reset_password_code = body["reset_password_code"]
        except KeyError:
            return make_response(
                success=False,
                message="Required field new_password or reset_password_code is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        reset_password_key = RESET_PASSWORD_CACHE_KEY.format(code=reset_password_code)
        user_id = await cache.get(reset_password_key)
        if user_id is None:
            return make_response(
                success=False,
                message="Required field reset_password_code is not correct or expired.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        validation_errors = validate_password(new_password)
        if validation_errors:
            return make_response(
                success=False,
                message=f"Invalid new password: {' '.join(validation_errors)}",
                http_status=HTTPStatus.BAD_REQUEST
            )

        password_hash = User.generate_password_hash(new_password)
        try:
            await User.update(int(user_id), password=password_hash)
        except DatabaseError:
            return make_response(
                success=False,
                message="The user password was not changed.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        await spawn(self.request, cache.delete(reset_password_key))

        return make_response(
            success=True,
            message="The user password was changed.",
            http_status=HTTPStatus.OK,
        )


@auth_routes.view("/v1/auth/change_email")
class AuthChangeEmailView(web.View):
    """Class that includes functionality to change user email."""

    async def post(self):
        """Send email changing confirmation to old user email."""
        body = self.request.body
        user_id = self.request.user_id

        try:
            new_email = body["new_email"]
        except KeyError:
            return make_response(
                success=False,
                message="Required field new_email is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        validation_errors = validate_email(new_email)
        if validation_errors:
            return make_response(
                success=False,
                message=' '.join(validation_errors),
                http_status=HTTPStatus.BAD_REQUEST
            )

        try:
            user = await User.get_by_id(user_id)
        except DatabaseError as err:
            return make_response(
                success=False,
                message=str(err),
                http_status=HTTPStatus.BAD_REQUEST
            )

        if user.email == new_email:
            return make_response(
                success=False,
                message="New email cannot be the same as your old email",
                http_status=HTTPStatus.BAD_REQUEST
            )

        change_email_code = str(uuid.uuid4())
        change_email_key = CHANGE_EMAIL_CACHE_KEY.format(code=change_email_code)
        change_email_cache_data = {"user_id": user_id, "new_email": new_email}
        await cache.set(change_email_key, change_email_cache_data, CHANGE_EMAIL_CACHE_EXPIRE)

        change_email_url = f"{self.request.url}/confirm?change_email_code={change_email_code}"
        await spawn(self.request, send_change_email_mail(user, new_email, str(change_email_url)))

        return make_response(
            success=True,
            message=f"The email with link for email changing confirmation "
                    f"should soon be delivered to {user.email}.",
            http_status=HTTPStatus.OK,
        )


@auth_routes.view("/v1/auth/change_email/confirm")
class AuthChangeEmailConfirmView(web.View):
    """Class that includes functionality to confirm user email changing."""

    async def get(self):
        """Return confirm response of user email changing."""
        # TODO: return errors as html too
        try:
            change_email_code = self.request.query["change_email_code"]
        except KeyError:
            return make_response(
                success=False,
                message="Required param change_email_code is not provided.",
                http_status=HTTPStatus.UNPROCESSABLE_ENTITY
            )

        change_email_key = CHANGE_EMAIL_CACHE_KEY.format(code=change_email_code)
        change_email_cache_data = await cache.get(change_email_key)
        if not change_email_cache_data:
            return make_response(
                success=False,
                message="Required query argument change_email_code is not correct or was expired.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        user_id, new_email = change_email_cache_data["user_id"], change_email_cache_data["new_email"]
        try:
            await User.update(user_id, email=new_email)
        except DatabaseError:
            return make_response(
                success=False,
                message="The user email was not updated.",
                http_status=HTTPStatus.BAD_REQUEST
            )

        return render_template(
            "change_email_confirm.html",
            self.request,
            {"new_email": new_email}
        )
