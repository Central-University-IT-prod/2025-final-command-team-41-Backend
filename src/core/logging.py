import logging
import sys
from typing import Any

from dishka import Provider, Scope, provide

from src.core.settings import Settings


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        extra_fields = ''
        if hasattr(record, 'extra'):
            extra = record.extra
            if isinstance(extra, dict):
                extra_fields = ' '.join(f'{k}={v}' for k, v in extra.items())  # type: ignore

        message = super().format(record)

        if extra_fields:
            message = f'{message} | {extra_fields}'

        return message


class LoggerProvider(Provider):
    @provide(scope=Scope.APP)
    def get_logger(self, settings: Settings) -> logging.Logger:
        root_logger = logging.getLogger()
        root_logger.setLevel(settings.environment_log_level)
        root_logger.handlers.clear()

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(settings.environment_log_level)

        formatter = CustomFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        return logging.getLogger('app')


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f'app.{name}')


def log_extra(**kwargs: Any) -> dict[str, Any]:
    return {'extra': kwargs}
