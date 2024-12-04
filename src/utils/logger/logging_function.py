from datetime import datetime, timezone
from functools import wraps
from typing import Callable
from uuid import uuid4

from aws_lambda_powertools import Logger


def logging_function(
    logger: Logger,
    *,
    write: bool = False,
    with_return: bool = False,
    with_args: bool = False,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper_function(*args, **kwargs):
            name_function = func.__name__
            id_call = str(uuid4())
            dt_start = datetime.now(tz=timezone.utc)
            result = None
            is_error = False
            try:
                data_start = {"FunctionName": name_function, "CallID": id_call}
                if with_args:
                    data_start["Args"] = args
                    data_start["KwArgs"] = kwargs
                if write:
                    logger.debug(
                        f'start function "{name_function}" ({id_call})', data=data_start
                    )
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                is_error = True
                logger.debug(
                    f"error occurred: {e}",
                    exc_info=True,
                    data={"ErrorType": str(type(e)), "ErrorMessage": str(e)},
                )
                raise
            finally:
                dt_end = datetime.now(tz=timezone.utc)
                delta = dt_end - dt_start
                data_end = {
                    "FunctionName": name_function,
                    "CallID": id_call,
                    "Duration": {
                        "str": str(delta),
                        "TotalSeconds": delta.total_seconds(),
                    },
                }
                if with_return and not is_error:
                    data_end["Return"] = result
                if with_args or is_error:
                    data_end["Args"] = args
                    data_end["KwArgs"] = kwargs
                if write or is_error:
                    status = "failed" if is_error else "succeeded"
                    logger.debug(
                        f'{status} function "{name_function}" ({id_call})',
                        data=data_end,
                    )

        return wrapper_function

    return decorator
