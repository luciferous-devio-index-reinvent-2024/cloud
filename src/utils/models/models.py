from __future__ import annotations

import json
from gzip import compress, decompress

from mypy_boto3_s3 import S3Client
from pydantic import BaseModel

from utils.logger import create_logger, logging_function

logger = create_logger(__name__)
KEY_CACHED_DATA = "data/cached_data.json.gzip"


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
    articles: dict[str, Article]
    authors: dict[str, Author]
    thumbnails: dict[str, str]
    list_published: list[str]

    @logging_function(logger)
    def to_json(self) -> str:
        data = CachedData(
            articles=self.articles,
            authors={k: self.authors[k] for k in sorted(self.authors.keys())},
            thumbnails={k: self.thumbnails[k] for k in sorted(self.thumbnails.keys())},
            list_published=sorted(self.list_published),
        )
        return data.model_dump_json()

    @logging_function(logger)
    def to_compressed_binary(self) -> bytes:
        text = self.to_json()
        return compress(text.encode())

    @logging_function(logger)
    def save(self, *, bucket: str, client: S3Client):
        client.put_object(
            Bucket=bucket,
            Key=KEY_CACHED_DATA,
            Body=self.to_compressed_binary(),
            ContentType="application/gzip",
        )

    @staticmethod
    @logging_function(logger)
    def load(*, bucket: str, client: S3Client) -> CachedData:
        try:
            resp = client.get_object(Bucket=bucket, Key=KEY_CACHED_DATA)
            binary = resp["Body"].read()
            decompressed = decompress(binary)
            return CachedData(**json.loads(decompressed))
        except client.exceptions.NoSuchKey:
            return CachedData(
                articles={},
                authors={},
                thumbnails={},
                list_published=[],
            )
