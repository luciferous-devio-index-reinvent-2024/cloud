import os
from functools import wraps
from typing import Callable

from aws_lambda_powertools import Logger

EXCLUDE_ENV_KEYS = {
    "AWS_ACCESS_KEY_ID",
    "AWS_LAMBDA_LOG_GROUP_NAME",
    "AWS_LAMBDA_LOG_STREAM_NAME",
    "AWS_LAMBDA_RUNTIME_API",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_SESSION_TOKEN",
    "AWS_XRAY_CONTEXT_MISSING",
    "AWS_XRAY_DAEMON_ADDRESS",
    "_AWS_XRAY_DAEMON_ADDRESS",
    "_AWS_XRAY_DAEMON_PORT",
}


def logging_handler(logger: Logger, *, with_return: bool = False) -> Callable:
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        @logger.inject_lambda_context()
        def process(event, context, *args, **kwargs):
            try:
                logger.debug(
                    "event and environment variables",
                    data={
                        "event": event,
                        "env": {
                            k: os.getenv(k)
                            for k in sorted(os.environ.keys())
                            if k not in EXCLUDE_ENV_KEYS
                        },
                    },
                )
            except Exception as e:
                logger.warning(
                    f"error occurred in logging event and environment variables: {e}",
                    exc_info=True,
                    data={"ErrorType": str(type(e)), "ErrorMessage": str(e)},
                )

            try:
                result = handler(event, context, *args, **kwargs)
                if with_return:
                    logger.debug("handler return", data={"Return": result})
                return result
            except Exception as e:
                logger.error(
                    f"error occurred in handler: {e}",
                    exc_info=True,
                    data={"ErrorType": str(type(e)), "ErrorMessage": str(e)},
                )

        return process

    return decorator
