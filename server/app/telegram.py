"""The module that provides telegram bot functionality."""

from aiogram import Bot
from aiogram.dispatcher import Dispatcher

from app import config


TELEGRAM_BOT = Bot(config.TELEGRAM_BOT_TOKEN)
TELEGRAM_DISPATCHER = Dispatcher(TELEGRAM_BOT)


# Telegram messages
TRY_LATER_TEXT = "Something bad happened. Please try again later."
TELEGRAM_BOT_ACTIVATED_TEXT = "You have successfully activated telegram bot for Spentless. " \
    "You will be notified for any occurred transactions and limit exceeding " \
    "in case you have enabled notification in our application."
INCORRECT_INVITATION_LINK_TEXT = "You have used incorrect invitation link. " \
   "Please use one that is provided in the Spentless mobile application."
EXPIRED_INVITATION_LINK_TEXT = "Your invitation was expired. " \
   "Please use new one in the Spentless mobile application."
