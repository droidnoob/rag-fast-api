from functools import lru_cache

from elasticsearch import Elasticsearch
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    env: str
    app_name: str
    version: str


class ElasticSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTIC_")

    host: str
    username: str
    password: str


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="OPENAI_")

    secret_key: str


app_settings = AppSettings()


@lru_cache
def get_elastic_client():
    settings = ElasticSettings()
    return Elasticsearch(
        hosts=settings.host,
        http_auth=(settings.username, settings.password),
    )
