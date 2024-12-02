import os
from dataclasses import fields

from utils.logger import create_logger, logging_function

logger = create_logger(__name__)


@logging_function(logger)
def load_environments[T](*, class_dataclass: type[T]) -> T:
    return class_dataclass(
        **{k.name: os.environ[k.name.upper()] for k in fields(class_dataclass)}
    )
