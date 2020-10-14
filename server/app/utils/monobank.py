"""This module provides interactions with monobank API."""

import logging
from datetime import datetime

import aiohttp

from app.models.mcc import MCC
from app.models.user import User
from app.models.transaction import Transaction
from app.utils.misc import retry
from app.utils.jwt import generate_token
from app.utils.errors import DatabaseError, RetryError


LOGGER = logging.getLogger(__name__)

MONOBANK_API = "https://api.monobank.ua"
MONOBANK_WEBHOOK_URL = f"{MONOBANK_API}/personal/webhook"
MONOBANK_USER_INFO_URL = f"{MONOBANK_API}/personal/client-info"
MONOBANK_USER_TRANSACTIONS_URL = f"{MONOBANK_API}/personal/statement/0/%s"


async def setup_webhook(user_id, user_monobank_token, collector_secret, collector_host):
    """Setup collector webhook for user based on id."""
    headers = {"X-Token": user_monobank_token}
    webhook_endpoint = f"{MONOBANK_API}/personal/webhook"
    user_collector_token, _ = generate_token(collector_secret, {"user_id": user_id})
    payload = {"webHookUrl": f"{collector_host}/monobank/{user_collector_token}"}
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_endpoint, headers=headers, json=payload) as response:
            return await response.json(), response.status


@retry(times=3)
async def save_user_monobank_info(user_id, user_monobank_token):
    """Retrieve user's data by his token from monobank API."""
    headers = {"X-Token": user_monobank_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(MONOBANK_USER_INFO_URL, headers=headers) as response:
            data, status = await response.json(), response.status

    if status != 200:
        LOGGER.error("Could not retrieve user`s=%s data from monobank. Error: %s", user_id, response)
        raise RetryError

    last_name, first_name = data.get("name", "").split(" ")
    try:
        await User.update(user_id, first_name=first_name, last_name=last_name, monobank_token=user_monobank_token)
        LOGGER.info("User=%s was successfully updated from monobank client info.", user_id)
    except DatabaseError:
        raise RetryError


@retry(times=3)
async def save_monobank_month_transactions(user_id, user_monobank_token):
    """
    Retrieve user's transactions by his token from monobank API
    that were made from the beginning of current month.
    """
    month_start_date = datetime.today().replace(day=1, hour=0, minute=0, second=0)
    month_start_timestamp = int(datetime.timestamp(month_start_date))
    headers = {"X-Token": user_monobank_token}
    async with aiohttp.ClientSession() as session:
        async with session.get(MONOBANK_USER_TRANSACTIONS_URL % month_start_timestamp, headers=headers) as response:
            data, status = await response.json(), response.status

    if status != 200:
        LOGGER.error("Could not retrieve user`s=%s transactions from monobank. Error: %s", user_id, data)
        raise RetryError

    try:
        mccs = await MCC.get_codes()
    except DatabaseError:
        raise RetryError

    def prepare_transaction(transaction):
        """Return formatted transaction."""
        costs_converter = 100.0

        mcc_code = transaction["mcc"]
        if mcc_code not in mccs:
            LOGGER.error("Could not find MCC code=%s in database.", mcc_code)
            mcc_code = -1

        return {
            "user_id": user_id,
            "id": transaction["id"],
            "amount": transaction["amount"] / costs_converter,
            "balance": transaction["balance"] / costs_converter,
            "cashback": transaction["cashbackAmount"] / costs_converter,
            "mcc": mcc_code,
            "timestamp": datetime.fromtimestamp(transaction["time"]),
            "info": transaction["description"],
        }

    transactions = [prepare_transaction(t) for t in data]

    await Transaction.create_bulk(transactions)
    LOGGER.info("User`s=%s transactions were loaded from monobank.", user_id)
