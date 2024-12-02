from dataclasses import dataclass, field
from uuid import uuid4

import boto3
from mypy_boto3_events import EventBridgeClient
from pytest import MonkeyPatch, fixture

LOCALSTACK_ENDPOINT_URL = "http://localhost:4566"


def create_uuid() -> str:
    return str(uuid4())


@dataclass
class DummyLambdaContext:
    function_name: str = field(default_factory=create_uuid)
    function_version: str = field(default_factory=create_uuid)
    invoked_function_arn: str = field(default_factory=create_uuid)
    memory_limit_in_mb: int = field(default=128)
    aws_request_id: str = field(default_factory=create_uuid)
    log_group_name: str = field(default_factory=create_uuid)
    log_stream_name: str = field(default_factory=create_uuid)
    identity: None = field(default=None)
    client_context: None = field(default=None)


@fixture(scope="function")
def dummy_context():
    return DummyLambdaContext()


@fixture(scope="function")
def set_environments(request, monkeypatch: MonkeyPatch):
    param: dict = request.param

    for k, v in param.items():
        monkeypatch.setenv(k, v)


@fixture(scope="session")
def client_events() -> EventBridgeClient:
    return boto3.client("events", endpoint_url=LOCALSTACK_ENDPOINT_URL)


@fixture(scope="function")
def events_event_bus(request, client_events):
    event_bus_name: str = request.param
    client_events.create_event_bus(Name=event_bus_name)
    yield
    client_events.delete_event_bus(Name=event_bus_name)
