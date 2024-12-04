from datetime import datetime
from http.client import HTTPResponse
from time import sleep
from typing import Callable
from urllib.request import Request, urlopen

from utils.logger import create_logger, logging_function

logger = create_logger(__name__)


def create_interval_getter(sec: float) -> Callable[[Request], HTTPResponse]:
    dt_prev = datetime(1992, 1, 26)

    @logging_function(logger)
    def request_http_get(req: Request) -> HTTPResponse:
        nonlocal dt_prev
        delta = datetime.now() - dt_prev
        interval = sec - delta.total_seconds()
        if interval > 0:
            sleep(interval)
        try:
            return urlopen(req)
        finally:
            dt_prev = datetime.now()

    return request_http_get
