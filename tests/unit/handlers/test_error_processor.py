import json

import pytest
from aws_lambda_powertools.utilities.data_classes.cloud_watch_logs_event import (
    CloudWatchLogsEvent,
    CloudWatchLogsLogEvent,
)
from freezegun import freeze_time

import handlers.error_processor.error_processor as index


class TestParseLogMessage:
    @pytest.mark.parametrize(
        "event, expected",
        [
            (
                CloudWatchLogsEvent(
                    {
                        "awslogs": {
                            "data": "H4sIAAAAAAAA/zWQy07dMBRFfyU66jAmx287syv1lkk7uhkVrpBjn0DUvBQ7hQrx7xWFzpf20l6vMFPO4ZG6PxtBC19P3enhx/lyOd2eoYb1eaEdWvBWo0ZhjEADNUzr4+2+Hhu00ITn3Exh7lNopiOOA+3rkVlYxjks8Yn1fWYplNCHTCxO65FYedoppMzSMW+0f8xdyk5hhhYECtWgajhv7r58P3XnS3eV0shBe20HjCoOMWjkFi2h9egFDVBDPvoc93Er47p8G6dCe4b2Do6FXjaKhRKjlzEXuP6znX/TUt6BVxgTtCAd98YrZVFKgxKVst6h5FJzK7QxqKQQRgnjrTUevbMCUXMBNZRxplzCvEHLLReOo5BOa17/D/v5iaFinHeoWmlb7m60xp9V4tIM0vQsYq+Z8soz50LPhLcoELnVQlRdyL+qd02q1qNUYSi0V9zhDccqU1yXlO+X+wXerm9/AVZ5B8DOAQAA"
                        }
                    }
                ),
                index.LogMessage(
                    lambda_request_id=None,
                    timestamp=1712810238551,
                    message="2024-04-11T04:37:18.550Z d136f36b-c0b5-4949-88ab-297020017522 Task timed out after 180.10 seconds\n\n",
                    error_message=None,
                ),
            ),
            (
                CloudWatchLogsEvent(
                    {
                        "awslogs": {
                            "data": "H4sIAAAAAAAA/61UXW/bNhT9KwQxIGknRaRFfRH7QIC6felWIPFblRkUee0IoUiNpJJ4Qf77IMn24q4L1mF8oaB77uHhvefyCXfgvdjCatcD5vjd5epy/cvy+vrywxJH2D4YcJjjqshIRhZ5viA5jrC22w/ODj3mOBEPPtGia5RI9CDbDTg7+FiYthNG3sZN42MlgmiEh1hqO6g43DoQysdq6HpwM911cCA6zPGCLFhCWEJp8vm7j5er5fXqhpVkozJRsiLNGWWLJhMsa1SmioowuhE4wn5ovHRtH1pr3rc6gPOYf8bgnHWxtlt8Mx2zvAcTxsgTbhXmOC1plVdpQauspIylaVoxlpdlxmiRZiylpMoqmhUpTcuC5hnNWZmSIsMRDm0HPoiux5wWdFGSqiK0IjQ6VBRz/FRjDfega8xrvLy6+nRV46jG2koxCp1+985K8J5n5RTbJ0+hST2yUg7OgUKtQbfCKA2OIyM6QGfLEXCGWo+MDUjBpjWgJpqjuoloLGpMWEzpijCeUs7oRVlV3xPCCZnwHtx9K+dj9/1Zz/2ZwtJqtfZBuFBjHtwAUY03g5HjLdajlinxP/V/4j9yddBZt1v79o+ZkpIFO0UIN9dNOMPFg+ez97joY2NduAXhQ0z5S8PyQy7/HwQ6+H0AH9atmlQUkGcLaMqYZFkWM0lkXDFWxSwtVLXI0iot5obAo4T+2PSVExIaIe/QeWd9QA4kmICk0Bpp4cMbXtcGofetBlTXNU5sH5J+F26tSaTtOmsSbbdbcNPWmu1674yLfjfiI6RbAyhLo9E1e4tNlAg58IMO6MeDmc5hHIoISWsCPIYIvRVu6yP09u3dw/j1Zp93XL/9y/XFFe6FS4Lwd8mpv04Vp7PivbSDYtF6QJPZz0dsAB/G/VTZ4cxfRQcT9tUpuUDvWoV2dkAdCMPR2afrGffzabv+cveRdx6YIOTdOox9rDF/qnHY9V/D3Qs9fIn4QWrhPTo7Is9+OsHW+NXxfh6fCasGPWObodWhNX72qRMd+Hp84Wq8afeQb7LP9EK1ZszM0hfWf/laHUoQoAMTpsi32wo/RyciXzHIC03p3zQdzPIVTf9oHPx8M5bx0Ynd3MTDQNM4z2mRF0LGOSlBNSwnlVK0XChWkCpjBavxc21Ggj8Bnrtc6D0HAAA="
                        }
                    }
                ),
                index.LogMessage(
                    lambda_request_id="7e652eb8-0555-4c0c-9449-437d9253937d",
                    timestamp=1712809901901,
                    message="error occurred in handler: name 'Error' is not defined",
                    error_message="[builtins.NameError] {'type': \"<class 'NameError'>\", 'value': \"name 'Error' is not defined\"}",
                ),
            ),
        ],
    )
    def test_normal(self, event, expected):
        decompressed_log = event.parse_logs_data()
        log_event = decompressed_log.log_events[0]
        actual = index.parse_message(log_event=log_event)
        assert actual == expected


class TestCreateUrlLambda:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "function_name": "luciferous-animanch-bbs-database-cloud-threads-dumper",
                    "region": "ap-northeast-1",
                },
                [
                    "https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/functions/luciferous-animanch-bbs-database-cloud-threads-dumper"
                ],
            )
        ],
    )
    def test_normal(self, option, expected):
        actual = index.create_url_lambda(**option)
        assert actual == expected[0]


class TestCreateUrlLogs:
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "log_group": "/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper",
                    "log_stream": "2024/04/11/[$LATEST]3363f5957f0c4cfca501707e079092ef",
                    "region": "ap-northeast-1",
                    "timestamp": 1712810238551,
                    "function_request_id": None,
                },
                [
                    "https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fluciferous-animanch-bbs-database-cloud-threads-dumper/log-events/2024$252F04$252F11$252F$255B$2524LATEST$255D3363f5957f0c4cfca501707e079092ef$3Fstart$3D1712809338551$26end$3D1712810248551"
                ],
            ),
            (
                {
                    "log_group": "/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper",
                    "log_stream": "2024/04/11/[$LATEST]480fd5a847364142b5a45bd5d79041fa",
                    "region": "ap-northeast-1",
                    "timestamp": 1712809901901,
                    "function_request_id": "7e652eb8-0555-4c0c-9449-437d9253937d",
                },
                [
                    "https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fluciferous-animanch-bbs-database-cloud-threads-dumper/log-events/2024$252F04$252F11$252F$255B$2524LATEST$255D480fd5a847364142b5a45bd5d79041fa$3FfilterPattern$3D$25227e652eb8-0555-4c0c-9449-437d9253937d$2522"
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.create_url_logs(**option)
        assert actual == expected[0]


class TestCreateSlackPayload:
    @freeze_time("2024-04-11 15:07:17.544914+09:00")
    @pytest.mark.parametrize(
        "option, expected",
        [
            (
                {
                    "log_group": "/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper",
                    "log_stream": "2024/04/11/[$LATEST]3363f5957f0c4cfca501707e079092ef",
                    "region": "ap-northeast-1",
                    "system_name": "test",
                    "log_event": CloudWatchLogsLogEvent(
                        {
                            "id": "38196944703360304479803135172566043226426977690987200512",
                            "timestamp": 1712810238551,
                            "message": "2024-04-11T04:37:18.550Z d136f36b-c0b5-4949-88ab-297020017522 Task timed out after 180.10 seconds\n\n",
                        }
                    ),
                },
                [
                    json.dumps(
                        {
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "<!channel> `2024-04-11 15:07:17.544914+09:00`",
                                    },
                                },
                                {"type": "divider"},
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*System Name:* `test`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Log Group:* `/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Log Stream:* `2024/04/11/[$LATEST]3363f5957f0c4cfca501707e079092ef`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Timestamp:* `1712810238551`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Datetime:* `2024-04-11 13:37:18.551000+09:00`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Lambda Console:* <https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/functions/luciferous-animanch-bbs-database-cloud-threads-dumper|link>",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*CloudWatch Logs Link:* <https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fluciferous-animanch-bbs-database-cloud-threads-dumper/log-events/2024$252F04$252F11$252F$255B$2524LATEST$255D3363f5957f0c4cfca501707e079092ef$3Fstart$3D1712809338551$26end$3D1712810248551|link>",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Message:*",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "```\n2024-04-11T04:37:18.550Z d136f36b-c0b5-4949-88ab-297020017522 Task timed out after 180.10 seconds\n\n\n```",
                                    },
                                },
                            ]
                        }
                    )
                ],
            ),
            (
                {
                    "log_group": "/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper",
                    "log_stream": "2024/04/11/[$LATEST]480fd5a847364142b5a45bd5d79041fa",
                    "region": "ap-northeast-1",
                    "system_name": "test",
                    "log_event": CloudWatchLogsLogEvent(
                        {
                            "id": "38196937195814433394468854173543109591573138716516483075",
                            "timestamp": 1712809901901,
                            "message": '{"level":"ERROR","location":"process:58","message":"error occurred in handler: name \'Error\' is not defined","timestamp":"2024-04-11T04:31:41.899+00:00","service":"threads_dumper","cold_start":true,"function_name":"luciferous-animanch-bbs-database-cloud-threads-dumper","function_memory_size":"1024","function_arn":"arn:aws:lambda:ap-northeast-1:975050266206:function:luciferous-animanch-bbs-database-cloud-threads-dumper","function_request_id":"7e652eb8-0555-4c0c-9449-437d9253937d","exception":"Traceback (most recent call last):\\n  File \\"/opt/python/common/logger/logging_handler.py\\", line 53, in process\\n    result = handler(event, context, *args, **kwargs)\\n             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\\n  File \\"/var/task/threads_dumper.py\\", line 33, in handler\\n    raise Error(\\"test\\")\\n          ^^^^^\\nNameError: name \'Error\' is not defined. Did you mean: \'OSError\'?","exception_name":"NameError","stack_trace":{"type":"NameError","value":{"type":"<class \'NameError\'>","value":"name \'Error\' is not defined"},"module":"builtins","frames":[{"file":"/opt/python/common/logger/logging_handler.py","line":53,"function":"process","statement":"result = handler(event, context, *args, **kwargs)"},{"file":"/var/task/threads_dumper.py","line":33,"function":"handler","statement":"raise Error(\\"test\\")"}]},"xray_trace_id":"1-661767ac-608edb4609dd182d47095474"}\n',
                        }
                    ),
                },
                [
                    json.dumps(
                        {
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "<!channel> `2024-04-11 15:07:17.544914+09:00`",
                                    },
                                },
                                {"type": "divider"},
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*System Name:* `test`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Log Group:* `/aws/lambda/luciferous-animanch-bbs-database-cloud-threads-dumper`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Log Stream:* `2024/04/11/[$LATEST]480fd5a847364142b5a45bd5d79041fa`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Timestamp:* `1712809901901`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Datetime:* `2024-04-11 13:31:41.901000+09:00`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Lambda Request ID:* `7e652eb8-0555-4c0c-9449-437d9253937d`",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Lambda Console:* <https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/functions/luciferous-animanch-bbs-database-cloud-threads-dumper|link>",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*CloudWatch Logs Link:* <https://ap-northeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-northeast-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fluciferous-animanch-bbs-database-cloud-threads-dumper/log-events/2024$252F04$252F11$252F$255B$2524LATEST$255D480fd5a847364142b5a45bd5d79041fa$3FfilterPattern$3D$25227e652eb8-0555-4c0c-9449-437d9253937d$2522|link>",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Message:*",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "```\nerror occurred in handler: name 'Error' is not defined\n```",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "*Error Message:*",
                                    },
                                },
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": "```\n[builtins.NameError] {'type': \"<class 'NameError'>\", 'value': \"name 'Error' is not defined\"}\n```",
                                    },
                                },
                            ]
                        }
                    )
                ],
            ),
        ],
    )
    def test_normal(self, option, expected):
        actual = index.create_slack_payload(**option)
        if actual != expected[0]:
            with open("tex.txt", "w") as f:
                f.write("\n".join([actual, expected[0]]))
        assert actual == expected[0]


class TestPutEvents:
    @pytest.mark.parametrize(
        "events_event_bus, option",
        [
            (
                "TestEventBus",
                {
                    "event_bus_name": "TestEventBus",
                    "messages": [
                        "1st",
                        "2nd",
                        "3rd",
                        "4th",
                        "5th",
                        "6th",
                        "7th",
                        "8th",
                        "9th",
                        "10th",
                        "11th",
                        "12th",
                        "13th",
                        "14th",
                        "15th",
                        "16th",
                        "17th",
                        "18th",
                        "19th",
                        "20th",
                        "21th",
                        "22th",
                    ],
                },
            )
        ],
        indirect=["events_event_bus"],
    )
    @pytest.mark.usefixtures("events_event_bus")
    def test_normal(self, client_events, option):
        index.put_events(client=client_events, **option)


class TestMain:
    @pytest.mark.parametrize(
        "events_event_bus, set_environments, event",
        [
            (
                "TestEventBus",
                {"EVENT_BUS_NAME": "TestEventBus", "SYSTEM_NAME": "test"},
                CloudWatchLogsEvent(
                    {
                        "awslogs": {
                            "data": "H4sIAAAAAAAA/zWQy07dMBRFfyU66jAmx287syv1lkk7uhkVrpBjn0DUvBQ7hQrx7xWFzpf20l6vMFPO4ZG6PxtBC19P3enhx/lyOd2eoYb1eaEdWvBWo0ZhjEADNUzr4+2+Hhu00ITn3Exh7lNopiOOA+3rkVlYxjks8Yn1fWYplNCHTCxO65FYedoppMzSMW+0f8xdyk5hhhYECtWgajhv7r58P3XnS3eV0shBe20HjCoOMWjkFi2h9egFDVBDPvoc93Er47p8G6dCe4b2Do6FXjaKhRKjlzEXuP6znX/TUt6BVxgTtCAd98YrZVFKgxKVst6h5FJzK7QxqKQQRgnjrTUevbMCUXMBNZRxplzCvEHLLReOo5BOa17/D/v5iaFinHeoWmlb7m60xp9V4tIM0vQsYq+Z8soz50LPhLcoELnVQlRdyL+qd02q1qNUYSi0V9zhDccqU1yXlO+X+wXerm9/AVZ5B8DOAQAA"
                        }
                    }
                ),
            ),
            (
                "TestEventBus",
                {"EVENT_BUS_NAME": "TestEventBus", "SYSTEM_NAME": "test"},
                CloudWatchLogsEvent(
                    {
                        "awslogs": {
                            "data": "H4sIAAAAAAAA/61UXW/bNhT9KwQxIGknRaRFfRH7QIC6felWIPFblRkUee0IoUiNpJJ4Qf77IMn24q4L1mF8oaB77uHhvefyCXfgvdjCatcD5vjd5epy/cvy+vrywxJH2D4YcJjjqshIRhZ5viA5jrC22w/ODj3mOBEPPtGia5RI9CDbDTg7+FiYthNG3sZN42MlgmiEh1hqO6g43DoQysdq6HpwM911cCA6zPGCLFhCWEJp8vm7j5er5fXqhpVkozJRsiLNGWWLJhMsa1SmioowuhE4wn5ovHRtH1pr3rc6gPOYf8bgnHWxtlt8Mx2zvAcTxsgTbhXmOC1plVdpQauspIylaVoxlpdlxmiRZiylpMoqmhUpTcuC5hnNWZmSIsMRDm0HPoiux5wWdFGSqiK0IjQ6VBRz/FRjDfega8xrvLy6+nRV46jG2koxCp1+985K8J5n5RTbJ0+hST2yUg7OgUKtQbfCKA2OIyM6QGfLEXCGWo+MDUjBpjWgJpqjuoloLGpMWEzpijCeUs7oRVlV3xPCCZnwHtx9K+dj9/1Zz/2ZwtJqtfZBuFBjHtwAUY03g5HjLdajlinxP/V/4j9yddBZt1v79o+ZkpIFO0UIN9dNOMPFg+ez97joY2NduAXhQ0z5S8PyQy7/HwQ6+H0AH9atmlQUkGcLaMqYZFkWM0lkXDFWxSwtVLXI0iot5obAo4T+2PSVExIaIe/QeWd9QA4kmICk0Bpp4cMbXtcGofetBlTXNU5sH5J+F26tSaTtOmsSbbdbcNPWmu1674yLfjfiI6RbAyhLo9E1e4tNlAg58IMO6MeDmc5hHIoISWsCPIYIvRVu6yP09u3dw/j1Zp93XL/9y/XFFe6FS4Lwd8mpv04Vp7PivbSDYtF6QJPZz0dsAB/G/VTZ4cxfRQcT9tUpuUDvWoV2dkAdCMPR2afrGffzabv+cveRdx6YIOTdOox9rDF/qnHY9V/D3Qs9fIn4QWrhPTo7Is9+OsHW+NXxfh6fCasGPWObodWhNX72qRMd+Hp84Wq8afeQb7LP9EK1ZszM0hfWf/laHUoQoAMTpsi32wo/RyciXzHIC03p3zQdzPIVTf9oHPx8M5bx0Ynd3MTDQNM4z2mRF0LGOSlBNSwnlVK0XChWkCpjBavxc21Ggj8Bnrtc6D0HAAA="
                        }
                    }
                ),
            ),
        ],
        indirect=["events_event_bus", "set_environments"],
    )
    @pytest.mark.usefixtures("events_event_bus", "set_environments")
    def test_normal(self, client_events, event):
        index.main(event=event, client_events=client_events)
