"""This module provides functionality to work with SMTP."""

import logging
from email.message import EmailMessage

import aiosmtplib
from jinja2 import Template

from app.config import SMTP_HOST, SMTP_LOGIN, SMTP_PASSWORD, EMAILS_DIR


LOGGER = logging.getLogger(__name__)

MAIL_SUBJECT = "Sheet Without Shit. {subject}"
RESET_PASSWORD_SUBJECT = "Reset Password"
RESET_PASSWORD_TEMPLATE = "reset_password.html"
CHANGE_EMAIL_SUBJECT = "Confirmation of Email changing"
CHANGE_EMAIL_TEMPLATE = "change_email.html"
USER_SIGNUP_SUBJECT = "Welcome aboard"
USER_SIGNUP_TEMPLATE = "user_signup.html"


def load_email_html(template_name):
    """Load html file to string from email dir by template name."""
    template_path = f"{EMAILS_DIR}/{template_name}"
    with open(template_path) as file:
        return Template(file.read())


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

    html_template = load_email_html(RESET_PASSWORD_TEMPLATE)
    html = html_template.render(reset_password_url=reset_password_url, username=username)
    message = create_email_message(user.email, RESET_PASSWORD_SUBJECT, html)

    await send_mail(message)


async def send_change_email_mail(user, new_email, change_email_url):
    """Send email with confirmation fo email changing to user."""
    username = user.first_name if user.first_name else user.email

    html_template = load_email_html(CHANGE_EMAIL_TEMPLATE)
    html = html_template.render(username=username, new_email=new_email, change_email_url=change_email_url)

    message = create_email_message(user.email, CHANGE_EMAIL_SUBJECT, html)

    await send_mail(message)


async def send_user_signup_mail(email):
    """Send email to user that have just signed up."""
    html_template = load_email_html(USER_SIGNUP_TEMPLATE)
    html = html_template.render()

    message = create_email_message(email, USER_SIGNUP_SUBJECT, html)

    await send_mail(message)
