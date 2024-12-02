import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from os.path import basename

from aws_cloudwatch_logs_url import create_url_log_events
from aws_lambda_powertools.logging.types import (
    PowertoolsLogRecord,
    PowertoolsStackTrace,
)
from aws_lambda_powertools.utilities.data_classes import (
    event_source,
)
from aws_lambda_powertools.utilities.data_classes.cloud_watch_logs_event import (
    CloudWatchLogsEvent,
    CloudWatchLogsLogEvent,
)

from utils.aws import create_client
from utils.dataclasses import load_environments
from utils.logger import create_logger, logging_function, logging_handler


@dataclass(frozen=True)
class EnvironmentVariables:
    event_bus_name: str
    aws_default_region: str
    system_name: str


@dataclass(frozen=True)
class LogMessage:
    lambda_request_id: str | None
    timestamp: int
    message: str
    error_message: str | None


JST = timezone(offset=timedelta(hours=+9), name="JST")
logger = create_logger(__name__)


@event_source(data_class=CloudWatchLogsEvent)
@logging_handler(logger)
def handler(event: CloudWatchLogsEvent, context):
    main(event=event)


@logging_function(logger)
def main(
    *,
    event: CloudWatchLogsEvent,
    client_events=create_client("events"),
):
    env = load_environments(class_dataclass=EnvironmentVariables)
    decompressed_log = event.parse_logs_data()
    messages = [
        create_slack_payload(
            log_group=decompressed_log.log_group,
            log_stream=decompressed_log.log_stream,
            region=env.aws_default_region,
            system_name=env.system_name,
            log_event=log_event,
        )
        for log_event in decompressed_log.log_events
    ]
    for i, m in enumerate(messages):
        logger.debug(f"log_event {i}", data={"index": i, "message": json.loads(m)})
    put_events(
        messages=messages, event_bus_name=env.event_bus_name, client=client_events
    )


@logging_function(logger)
def parse_message(*, log_event: CloudWatchLogsLogEvent):
    try:
        data: PowertoolsLogRecord = json.loads(log_event.message)
    except Exception:
        return LogMessage(
            lambda_request_id=None,
            timestamp=log_event.timestamp,
            message=log_event.message[:300],
            error_message=None,
        )

    if "stack_trace" in data:
        stack_trace: PowertoolsStackTrace = data["stack_trace"]
        return LogMessage(
            lambda_request_id=data.get("function_request_id"),
            timestamp=log_event.timestamp,
            message=str(data["message"])[:300],
            error_message="[{0}.{1}] {2}".format(
                stack_trace["module"], stack_trace["type"], stack_trace["value"]
            )[:300],
        )
    else:
        return LogMessage(
            lambda_request_id=data.get("function_request_id"),
            timestamp=log_event.timestamp,
            message=str(data["message"])[:300],
            error_message=None,
        )


@logging_function(logger)
def create_url_lambda(*, function_name: str, region: str) -> str:
    return "".join(
        [
            "https://",
            region,
            ".console.aws.amazon.com/lambda/home?region=",
            region,
            "#/functions/",
            function_name,
        ]
    )


@logging_function(logger)
def create_url_logs(
    *,
    region: str,
    log_group: str,
    log_stream: str,
    timestamp: int,
    function_request_id: str | None,
) -> str:
    if function_request_id is None:
        start = timestamp - 900_000  # 1000 ms/s * 60 s/m * 15 m = 900,000 ms
        end = timestamp + 10_000
        return create_url_log_events(
            region=region,
            log_group_name=log_group,
            log_stream_name=log_stream,
            start=start,
            end=end,
        )
    else:
        return create_url_log_events(
            region=region,
            log_group_name=log_group,
            log_stream_name=log_stream,
            filter_pattern=f'"{function_request_id}"',
        )


@logging_function(logger)
def create_slack_payload(
    *,
    log_group: str,
    log_stream: str,
    region: str,
    system_name: str,
    log_event: CloudWatchLogsLogEvent,
) -> str:
    function_name = basename(log_group)
    log_message = parse_message(log_event=log_event)
    url_lambda = create_url_lambda(function_name=function_name, region=region)
    url_logs = create_url_logs(
        region=region,
        log_group=log_group,
        log_stream=log_stream,
        timestamp=log_message.timestamp,
        function_request_id=log_message.lambda_request_id,
    )
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"<!channel> `{datetime.now(tz=JST)}`"},
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*System Name:* `{system_name}`"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Log Group:* `{log_group}`"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Log Stream:* `{log_stream}`"},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Timestamp:* `{log_event.timestamp}`"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Datetime:* `{0}`".format(
                    datetime.fromtimestamp(log_event.timestamp / 1000, tz=JST)
                ),
            },
        },
    ]

    if log_message.lambda_request_id is not None:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Lambda Request ID:* `{log_message.lambda_request_id}`",
                },
            }
        )

    blocks += [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Lambda Console:* <{url_lambda}|link>",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*CloudWatch Logs Link:* <{url_logs}|link>",
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Message:*"}},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "```\n{0}\n```".format(log_message.message),
            },
        },
    ]

    if log_message.error_message is not None:
        blocks += [
            {"type": "section", "text": {"type": "mrkdwn", "text": "*Error Message:*"}},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "```\n{0}\n```".format(log_message.error_message),
                },
            },
        ]

    return json.dumps({"blocks": blocks})


@logging_function(logger)
def put_events(*, messages: list[str], event_bus_name: str, client):
    mapping_messages = {str(i): x for i, x in enumerate(messages)}
    union_succeeded = set()
    union_all = set(mapping_messages.keys())

    while union_succeeded != union_all:
        entries = []
        keys = []
        for k, v in mapping_messages.items():
            if len(entries) == 10:
                break
            if k in union_succeeded:
                continue
            keys.append(k)
            entries.append(
                {
                    "Source": "a",
                    "DetailType": "a",
                    "Detail": v,
                    "EventBusName": event_bus_name,
                }
            )

        resp = client.put_events(Entries=entries)
        failed_keys = []
        for k, entry in zip(keys, resp["Entries"]):
            if "EventId" in entry:
                union_succeeded.add(k)
            else:
                failed_keys.append(k)

        if len(failed_keys) > 0:
            logger.warning("failed to put events", data={"failed index": failed_keys})
            raise RuntimeError("has entries failed to put events")
