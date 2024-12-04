import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import cache
from gzip import compress, decompress
from hashlib import sha256
from urllib.request import Request

from mypy_boto3_s3 import S3Client
from mypy_boto3_ssm import SSMClient
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from utils.aws import create_client
from utils.http import client_contentful, client_notion
from utils.logger import create_logger, logging_function, logging_handler

jst = timezone(offset=timedelta(hours=+9), name="JST")
logger = create_logger(__name__)
KEY_CACHED_DATA = "data/cached_data.json.gzip"


class EnvironmentVariables(BaseSettings):
    ssm_parameter_name_token_contentful: str
    ssm_parameter_name_notion_database_id: str
    ssm_parameter_name_notion_token: str
    bucket_name_data: str


@dataclass(frozen=True)
class SsmParameters:
    token_contentful: str
    notion_database_id: str
    notion_token: str


class Author(BaseModel):
    url: str
    name: str
    avatar: str


class Article(BaseModel):
    url: str
    thumbnail: str
    title: str
    date: str
    raw_date: str
    author: Author


class CachedData(BaseModel):
    articles: list[Article]
    authors: dict[str, Author]
    thumbnails: dict[str, str]
    list_inserted: list[str]
    list_published: list[str]
    hash_inserted: str
    hash_published: str

    @logging_function(logger)
    def calc_hash_inserted(self) -> str:
        array = sorted(self.list_inserted)
        text = json.dumps(array)
        return sha256(text.encode()).hexdigest()

    @logging_function(logger)
    def calc_hash_published(self) -> str:
        array = sorted(self.list_published)
        text = json.dumps(array)
        return sha256(text.encode()).hexdigest()

    @logging_function(logger)
    def to_json(self) -> str:
        data = CachedData(
            articles=self.articles,
            authors={k: self.authors[k] for k in sorted(self.authors.keys())},
            thumbnails={k: self.thumbnails[k] for k in sorted(self.thumbnails.keys())},
            list_inserted=sorted(self.list_inserted),
            list_published=sorted(self.list_published),
            hash_inserted="",
            hash_published="",
        )
        data.hash_inserted = data.calc_hash_inserted()
        data.hash_published = data.calc_hash_published()
        return data.model_dump_json()

    @logging_function(logger)
    def to_compressed_binary(self) -> bytes:
        text = self.to_json()
        return compress(text.encode())


@logging_handler(logger)
def handler(event, context):
    main()


@logging_function(logger)
def main(
    *,
    client_ssm: SSMClient = create_client("ssm"),
    client_s3: S3Client = create_client("s3"),
):
    # noinspection PyArgumentList
    env = EnvironmentVariables()
    params = get_ssm_parameters(
        name_token_contentful=env.ssm_parameter_name_token_contentful,
        name_notion_database_id=env.ssm_parameter_name_notion_database_id,
        name_notion_token=env.ssm_parameter_name_notion_token,
        client=client_ssm,
    )
    cached_data = load_cached_data(bucket=env.bucket_name_data, client=client_s3)
    articles = get_articles(
        cached_data=cached_data, token_contentful=params.token_contentful
    )
    for ar in articles:
        insert_to_database(
            article=ar,
            notion_database_id=params.notion_database_id,
            notion_token=params.notion_token,
        )
        cached_data.articles.append(ar)
        cached_data.list_inserted.append(ar.url)
    save_cache(cached_data=cached_data, bucket=env.bucket_name_data, client=client_s3)


@logging_function(logger)
def internal_get_ssm_parameters(
    *,
    name_token_contentful: str,
    name_notion_database_id: str,
    name_notion_token: str,
    client: SSMClient,
) -> SsmParameters:
    resp = client.get_parameters(
        Names=[name_token_contentful, name_notion_database_id, name_notion_token],
        WithDecryption=True,
    )
    mapping = {x["Name"]: x["Value"] for x in resp["Parameters"]}
    return SsmParameters(
        token_contentful=mapping[name_token_contentful],
        notion_database_id=mapping[name_notion_database_id],
        notion_token=mapping[name_notion_token],
    )


@logging_function(logger)
@cache
def get_ssm_parameters(
    *,
    name_token_contentful: str,
    name_notion_database_id: str,
    name_notion_token: str,
    client: SSMClient,
) -> SsmParameters:
    return internal_get_ssm_parameters(
        name_token_contentful=name_token_contentful,
        name_notion_database_id=name_notion_database_id,
        name_notion_token=name_notion_token,
        client=client,
    )


@logging_function(logger)
def load_cached_data(*, bucket: str, client: S3Client) -> CachedData:
    try:
        resp = client.get_object(Bucket=bucket, Key=KEY_CACHED_DATA)
        binary = resp["Body"].read()
        decompressed = decompress(binary)
        return CachedData(**json.loads(decompressed))
    except client.exceptions.NoSuchKey:
        return CachedData(
            articles=[],
            authors={},
            thumbnails={},
            list_inserted=[],
            list_published=[],
            hash_inserted="",
            hash_published="",
        )


@logging_function(logger)
def get_thumbnail_url(*, thumbnail_id: str, token_contentful: str) -> str:
    url = f"https://api.contentful.com/spaces/ct0aopd36mqt/environments/master/assets/{thumbnail_id}"
    req = Request(url=url, headers={"Authorization": f"Bearer {token_contentful}"})
    resp = client_contentful(req)
    binary = resp.read()
    data = json.loads(binary)
    return data["fields"]["file"]["en-US"]["url"]


@logging_function(logger)
def get_author(*, author_id: str, token_contentful: str) -> Author:
    url = f"https://api.contentful.com/spaces/ct0aopd36mqt/environments/master/entries?sys.id={author_id}&content_type=authorProfile"
    req = Request(url=url, headers={"Authorization": f"Bearer {token_contentful}"})
    resp = client_contentful(req)
    binary = resp.read()
    data = json.loads(binary)
    item = data["items"][0]
    return Author(
        url="https://dev.classmethod.jp/author/{}/".format(
            item["fields"]["slug"]["en-US"]
        ),
        name=item["fields"]["displayName"]["en-US"],
        avatar=item["fields"]["thumbnail"]["en-US"],
    )


@logging_function(logger)
def resolve_thumbnail_url(*, item: dict) -> tuple[bool, str]:
    try:
        return False, item["fields"]["wpThumbnail"]["en-US"]
    except KeyError:
        return True, item["fields"]["thumbnail"]["en-US"]["sys"]["id"]


@logging_function(logger)
def convert_article(
    *, item: dict, cached_data: CachedData, token_contentful: str
) -> Article:
    dt_utc = datetime.strptime(
        item["sys"]["createdAt"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    dt_jst = dt_utc.astimezone(jst)

    is_thumbnail_id, thumbnail_value = resolve_thumbnail_url(item=item)
    if is_thumbnail_id:
        if thumbnail_value in cached_data.thumbnails:
            thumbnail_value = cached_data.thumbnails[thumbnail_value]
        else:
            thumbnail_url = get_thumbnail_url(
                thumbnail_id=thumbnail_value, token_contentful=token_contentful
            )
            cached_data.thumbnails[thumbnail_value] = thumbnail_url
            thumbnail_value = thumbnail_url

    author_id = item["fields"]["author"]["en-US"]["sys"]["id"]
    info_author = cached_data.authors.get(author_id)
    if info_author is None:
        info_author = get_author(author_id=author_id, token_contentful=token_contentful)
        cached_data.authors[author_id] = info_author

    return Article(
        url="https://dev.classmethod.jp/articles/{}/".format(
            item["fields"]["slug"]["en-US"]
        ),
        thumbnail=thumbnail_value,
        title=item["fields"]["title"]["en-US"],
        raw_date=str(dt_jst),
        date=dt_jst.strftime("%Y.%m.%d"),
        author=info_author,
    )


@logging_function(logger)
def get_articles(*, cached_data: CachedData, token_contentful: str) -> list[Article]:
    count = -1
    length = 0
    limit = 100
    headers = {"Authorization": f"Bearer {token_contentful}"}
    result = []
    while True:
        count += 1
        url = f"https://api.contentful.com/spaces/ct0aopd36mqt/environments/master/entries?fields.referenceCategory.en-US.sys.id=1DdS3IwWwqYx0N3Vwtn0e6&content_type=blogPost&limit={limit}&skip={limit * count}"
        req = Request(url=url, headers=headers)
        resp = client_contentful(req)
        binary = resp.read()
        data = json.loads(binary)
        all_items = data["items"]
        for item in all_items:
            article = convert_article(
                item=item, cached_data=cached_data, token_contentful=token_contentful
            )
            if article.url in cached_data.list_inserted:
                return result
            result.append(article)
        length += len(all_items)
        total = data["total"]
        if total == length:
            return result


@logging_function(logger)
def insert_to_database(*, article: Article, notion_database_id: str, notion_token: str):
    req = Request(
        url="https://api.notion.com/v1/pages",
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
            "Authorization": f"Bearer {notion_token}",
        },
        data=json.dumps(
            {
                "parent": {"database_id": notion_database_id},
                "properties": {
                    "Title": {"title": [{"text": {"content": article.title}}]},
                    "URL": {"url": article.url},
                    "Date": {"rich_text": [{"text": {"content": article.date}}]},
                    "RawDate": {"rich_text": [{"text": {"content": article.raw_date}}]},
                    "AuthorId": {"number": 1},
                    "AuthorName": {
                        "rich_text": [{"text": {"content": article.author.name}}]
                    },
                    "AuthorUrl": {"url": article.author.url},
                    "PostId": {"number": 1},
                    "Thumbnail": {"url": article.thumbnail},
                },
            }
        ).encode(),
    )
    client_notion(req)


@logging_function(logger)
def save_cache(*, cached_data: CachedData, bucket: str, client: S3Client):
    client.put_object(
        Bucket=bucket,
        Key=KEY_CACHED_DATA,
        Body=cached_data.to_compressed_binary(),
        ContentType="application/gzip",
    )
