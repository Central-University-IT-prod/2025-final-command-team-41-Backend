import pathlib
import typing
from enum import StrEnum

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class S3(BaseModel):
    access_key_id: str
    access_key: str
    bucket: str


class Runner(BaseModel):
    workers: int


class Server(BaseModel):
    port: int
    workers: int
    root_path: str


class Postgres(BaseModel):
    user: str
    password: str
    db: str
    host: str
    port: str

    provider: str = 'postgresql+asyncpg'

    @property
    def url(self) -> str:
        return f'{self.provider}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}'

    @property
    def url_localhost(self) -> str:
        return f'{self.provider}://{self.user}:{self.password}@localhost:{self.port}/{self.db}'


class Jwt(BaseModel):
    secret: str
    algorithm: str = Field(default='HS256')
    expire: int = Field(default=12000)


class Firebase(BaseModel):
    project_id: str
    credentials_file: str
    type: str = Field(default='service_account')
    database_url: str = Field(default='')

    def model_post_init(self, _: typing.Any) -> None:
        if not pathlib.Path(self.credentials_file).exists():
            msg = f'Firebase credentials file not found at {self.credentials_file}'
            raise ValueError(
                msg,
            )


class Rabbitmq(BaseModel):
    host: str = Field(default='rabbitmq')
    port: int = Field(default=5672)
    user: str = Field(default='guest')
    password: str = Field(default='guest')
    vhost: str = Field(default='/')
    use: bool = Field(default=False)


class Log(BaseModel):
    level: str = Field(default='INFO')
    format: str = Field(default='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Settings(BaseSettings):
    environment: Environment = Field(default=Environment.DEVELOPMENT)

    runner: Runner
    server: Server
    bus_exceptions: bool = Field(default=False)
    postgres: Postgres
    jwt: Jwt
    firebase: Firebase

    rabbitmq: Rabbitmq
    log: Log

    s3: S3

    @property
    def environment_log_level(self) -> str:
        log_levels: dict[Environment, str] = {
            Environment.DEVELOPMENT: 'DEBUG',
            Environment.STAGING: 'INFO',
            Environment.PRODUCTION: 'WARNING',
        }
        return log_levels.get(self.environment, self.log.level)

    model_config = SettingsConfigDict(
        env_file='.env',
        env_nested_delimiter='__',
        case_sensitive=False,
        extra='ignore',
    )


def get_settings() -> Settings:
    return Settings()  # type: ignore
