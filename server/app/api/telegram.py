"""This module provides handlers for telegram bot webhook messages."""

from app.cache import cache, TELEGRAM_CACHE_KEY
from app.models.user import User
from app.utils.errors import DatabaseError, DBNoResultFoundError
from app.telegram import (
    TELEGRAM_BOT,
    INCORRECT_INVITATION_LINK_TEXT,
    EXPIRED_INVITATION_LINK_TEXT,
    TRY_LATER_TEXT,
    ACTIVATED_TEXT,
    DEACTIVATED_TEXT,
    ALREADY_DEACTIVATED_TEXT
)


async def handle_start(message):
    """
    Handle start telegram bot command.
    Updates user`s telegram id.
    """
    telegram_id = message.chat.id
    _, telegram_cache_code = message.text.replace(" ", "").split("/start")
    if not telegram_cache_code:
        await TELEGRAM_BOT.send_message(telegram_id, INCORRECT_INVITATION_LINK_TEXT)
        return

    telegram_cache_key = TELEGRAM_CACHE_KEY.format(code=telegram_cache_code)
    user_id = await cache.get(telegram_cache_key)
    if user_id is None:
        await TELEGRAM_BOT.send_message(telegram_id, EXPIRED_INVITATION_LINK_TEXT)
        return

    try:
        await User.update(user_id, telegram_id=telegram_id)
    except DatabaseError:
        await TELEGRAM_BOT.send_message(telegram_id, TRY_LATER_TEXT)
        return
    else:
        await TELEGRAM_BOT.send_message(telegram_id, ACTIVATED_TEXT)

    await cache.delete(telegram_cache_key)


async def handle_stop(message):
    """
    Handle stop telegram bot command.
    Deletes user`s telegram id.
    """
    telegram_id = message.chat.id

    try:
        user = await User.get_by_telegram_id(telegram_id)
    except DBNoResultFoundError:
        await TELEGRAM_BOT.send_message(telegram_id, ALREADY_DEACTIVATED_TEXT)
        return
    except DatabaseError:
        await TELEGRAM_BOT.send_message(telegram_id, TRY_LATER_TEXT)
        return

    try:
        await User.update(user.id, telegram_id=telegram_id)
    except DatabaseError:
        await TELEGRAM_BOT.send_message(telegram_id, TRY_LATER_TEXT)
        return
    else:
        await TELEGRAM_BOT.send_message(telegram_id, DEACTIVATED_TEXT)
