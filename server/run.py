import os

from aiohttp.web import run_app

from app.main import init_app


ACCESS_LOG_FORMAT = "%a [VIEW: %r] [RESPONSE: %s (%bb)] [TIME: %Dms]"


if __name__ == '__main__':
    host = os.environ.get("SERVER_HOST", "localhost")

    run_app(
        init_app(),
        host=host,
        port=5000,
        access_log_format=ACCESS_LOG_FORMAT
    )
