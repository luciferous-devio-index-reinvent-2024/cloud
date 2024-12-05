from base64 import b64encode
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from gzip import compress
from logging import DEBUG
from urllib.request import Request

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes.common import DictWrapper
from pydantic import BaseModel


def custom_default(obj):
    if isinstance(obj, tuple):
        return list(obj)
    if isinstance(obj, set):
        return {"type": str(type(obj)), "values": list(obj)}
    if isinstance(obj, datetime):
        return str(obj)
    if isinstance(obj, bytes):
        compressed = compress(obj, compresslevel=7)
        encoded = b64encode(compressed).decode()
        return {"type": "bytes (base64 encoded, gzip compressed)", "value": encoded}
    if isinstance(obj, Decimal):
        return num if (num := int(obj)) == obj else float(str(obj))
    if isinstance(obj, DictWrapper):
        return obj.raw_event
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if isinstance(obj, Request):
        return {
            "type": str(type(obj)),
            "value": {
                "url": obj.full_url,
                "method": obj.method,
                "headers": obj.headers,
                "data": obj.data,
            },
        }
    if is_dataclass(obj):
        if isinstance(obj, type):
            return {"type": str(obj)}
        else:
            return asdict(obj)
    try:
        return {"type": str(type(obj)), "value": str(obj)}
    except Exception as e:
        return {
            "type": str(type(obj)),
            "error": {"type": str(type(e)), "message": str(e)},
        }


def create_logger(name: str) -> Logger:
    return Logger(
        service=name, level=DEBUG, use_rfc3339=True, json_default=custom_default
    )
