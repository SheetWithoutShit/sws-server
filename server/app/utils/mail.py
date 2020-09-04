"""This module provides functionality to work with SMTP."""

import logging
from email.message import EmailMessage

import aiosmtplib

from app.config import SMTP_HOST, SMTP_LOGIN, SMTP_PASSWORD


LOGGER = logging.getLogger(__name__)

MAIL_SUBJECT = "Sheet Without Shit. {subject}"
RESET_PASSWORD_SUBJECT = "Reset Password"
CHANGE_EMAIL_SUBJECT = "Confirmation of Email changing"
USER_SIGNUP_SUBJECT = "Welcome aboard"
RESET_PASSWORD_MAIL = """
    <html>
    <head></head>
    <body style="color: #209F85">
        <h1>Hi, {username}.</h1>
        <p>A password reset for your account was requested.</p>
        <p>Please click the button below to change your password.</p>
        <p>Note that this link is valid for 24 hours.</p>
        <p>After the time limit has expired, you will have to resubmit the request for a password reset.</p>
        <button style="color: #209F85" id="change-password-button">
            <a style="color: #209F85" href={reset_password_url}>Change Your Password</a>
        </button>
    </body>
    </html>
"""
CHANGE_EMAIL_MAIL = """
    <html>
    <head></head>
    <body style="color: #209F85">
        <h1>Hi, {username}.</h1>
        <p>We would like to confirm that you prefer using {new_email} as your email.</p>
        <p>In case you don't want to change your current email - ignore this message.</p>
        <p>In order to confirm the email changing, you need to click the button below.<p/>
        <p>Note that this link is valid for 48 hours.</p>
        <p>After the time limit has expired, you will have to resubmit the request for an email changing.</p>
        <button style="color: #209F85" id="change-email-button">
            <a style="color: #209F85" href={change_email_url}>Confirm</a>
        </button>
    </body>
    </html>
"""
USER_SIGNUP_MAIL = """
    <html>
    <head></head>
    <body style="color: #209F85">
        <p>Congratulations!</p>
        <p>You have successfully signed up.</p>
        <p>We are happy to see you as a member of SheetWithoutShit application.</p>
        <p>Our system will help you to save your costs and control all your transactions.<p/>
        <p>Also, we have a lot of other interesting features.</p>
        <p>Do not waste time - let's configure your budget!</p>
    </body>
    </html>
"""


def create_email_message(receiver, subject, html):
    """Create dummy email message."""
    message = EmailMessage()

    message["From"] = SMTP_LOGIN
    message["To"] = receiver
    message["Subject"] = MAIL_SUBJECT.format(subject=subject)

    message.add_alternative(html, subtype="html")

    return message


async def send_mail(message):
    """Send email message via gmail smtp service."""
    smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=587, use_tls=False)

    await smtp.connect()
    await smtp.starttls()
    await smtp.login(SMTP_LOGIN, SMTP_PASSWORD)

    try:
        await smtp.send_message(message)
    except aiosmtplib.errors.SMTPException as err:
        LOGGER.error("Could not send email to user. Error: %s", str(err))


async def send_reset_password_mail(user, reset_password_url):
    """Send reset password email message to user."""
    username = user.first_name if user.first_name else user.email

    html = RESET_PASSWORD_MAIL.format(username=username, reset_password_url=reset_password_url)
    message = create_email_message(user.email, RESET_PASSWORD_SUBJECT, html)

    await send_mail(message)


async def send_change_email_mail(user, new_email, change_email_url):
    """Send email with confirmation fo email changing to user."""
    username = user.first_name if user.first_name else user.email

    html = CHANGE_EMAIL_MAIL.format(username=username, new_email=new_email, change_email_url=change_email_url)
    message = create_email_message(user.email, CHANGE_EMAIL_SUBJECT, html)

    await send_mail(message)


async def send_user_signup_mail(email):
    """Send email to user that have just signed up."""
    message = create_email_message(email, USER_SIGNUP_SUBJECT, USER_SIGNUP_MAIL)

    await send_mail(message)
