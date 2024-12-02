import boto3
from boto3.resources.base import ServiceResource
from botocore.client import BaseClient
from botocore.config import Config

from utils.logger import create_logger, logging_function

BOTOCORE_CONFIG_DEFAULT = Config(
    connect_timeout=5, read_timeout=5, retries={"mode": "standard"}
)

logger = create_logger(__name__)


@logging_function(logger)
def create_client(name: str, *, config: Config | None = None, **kwargs) -> BaseClient:
    return boto3.client(
        name, config=BOTOCORE_CONFIG_DEFAULT if config is None else config, **kwargs
    )


@logging_function(logger)
def create_resource(
    name: str, *, config: Config | None = None, **kwargs
) -> ServiceResource:
    return boto3.resource(
        name, config=BOTOCORE_CONFIG_DEFAULT if config is None else config, **kwargs
    )
