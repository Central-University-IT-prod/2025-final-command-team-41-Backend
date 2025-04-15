import contextlib
import json
import typing
from asyncio import create_task, gather
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    Protocol,
    runtime_checkable,
)
from uuid import UUID

import aio_pika
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
)
from aio_pika.exchange import ExchangeType

from src.core.logging import get_logger, log_extra
from src.core.settings import Settings

logger = get_logger(__name__)

# Тип для обработчиков событий
EventHandler = Callable[[Any], Awaitable[None]]


def serialize_datetime(obj: Any) -> Any:
    """Сериализует объекты datetime в ISO формат и UUID в строки для JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    msg = f'Object of type {obj.__class__.__name__} is not JSON serializable'
    raise TypeError(msg)


def deserialize_datetime(data: dict[str, Any]) -> dict[str, Any]:
    """Десериализует ISO формат строк обратно в объекты datetime и строки UUID в объекты UUID."""
    for key, value in data.items():
        if isinstance(value, str):
            try:
                data[key] = datetime.fromisoformat(value)
            except ValueError:
                # Try to convert to UUID if it looks like a UUID
                if key.endswith('_id') or key == 'id':
                    with contextlib.suppress(ValueError):
                        data[key] = UUID(value)
                # If the string is not in ISO format, leave it as is
    return data


async def handle_event_safely(handler: EventHandler, event: Any) -> None:
    """Вызывает асинхронный обработчик события с обработкой исключений."""
    try:
        await handler(event)
    except Exception:
        logger.exception('Error in event handler')


@dataclass
class EventSubscription:
    """Хранит подписку на событие с типом события и обработчиком."""

    event_type: type[Any]
    handler: EventHandler


@runtime_checkable
class EventBus(Protocol):
    """Протокол для шины событий."""

    async def subscribe(self, event_type: type[Any], handler: EventHandler) -> None: ...
    async def unsubscribe(
        self,
        event_type: type[Any],
        handler: EventHandler,
    ) -> None: ...
    async def publish(self, event: Any) -> None: ...
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...


class InMemoryEventBus:
    """Реализация шины событий в памяти."""

    def __init__(self, raise_exceptions: bool = False) -> None:  # noqa
        self._subscriptions: dict[str, list[EventSubscription]] = {}
        self._active = True
        self._raise_exceptions = raise_exceptions

    async def connect(self) -> None:
        """Заглушка для метода подключения."""

    async def disconnect(self) -> None:
        """Заглушка для метода отключения."""

    async def subscribe(self, event_type: type[Any], handler: EventHandler) -> None:
        """Подписывает обработчик на событие."""
        event_name = event_type.__name__
        if event_name not in self._subscriptions:
            self._subscriptions[event_name] = []
        self._subscriptions[event_name].append(EventSubscription(event_type, handler))

    async def unsubscribe(self, event_type: type[Any], handler: EventHandler) -> None:
        """Отписывает обработчик от события."""
        event_name = event_type.__name__
        if event_name in self._subscriptions:
            self._subscriptions[event_name] = [
                sub for sub in self._subscriptions[event_name] if sub.handler != handler
            ]

    async def publish(self, event: Any) -> None:
        """Публикует событие, вызывая все подписанные обработчики асинхронно."""
        if not self._active:
            return
        event_name = event.__class__.__name__
        if event_name not in self._subscriptions:
            return
        for subscription in self._subscriptions[event_name]:
            await create_task(self._process_event(subscription, event))

    async def _process_event(self, subscription: EventSubscription, event: Any) -> None:
        """Обрабатывает событие, вызывая соответствующий обработчик."""
        await handle_event_safely(subscription.handler, event)
        # Если raise_exceptions=True, исключения уже залогированы в handle_event_safely,
        # но здесь мы их не пробрасываем дальше, чтобы не прерывать другие обработчики

    @asynccontextmanager
    async def pause(self) -> None:
        """Контекстный менеджер для временной приостановки публикации событий."""
        prev_state = self._active
        self._active = False
        try:
            yield
        finally:
            self._active = prev_state


class RabbitMQEventBus:
    """Реализация шины событий с использованием RabbitMQ."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None
        self._subscriptions: dict[str, list[EventSubscription]] = {}
        self._consumer_tags: dict[
            str,
            str,
        ] = {}  # Хранит теги потребителей для каждого события
        self._active = True
        self._queues: dict[str, AbstractQueue] = {}

    async def connect(self) -> None:
        """Устанавливает соединение с RabbitMQ."""
        if self._connection is None:
            self._connection = await aio_pika.connect_robust(
                host=self.settings.rabbitmq.host,
                port=self.settings.rabbitmq.port,
                login=self.settings.rabbitmq.user,
                password=self.settings.rabbitmq.password,
                virtualhost=self.settings.rabbitmq.vhost,
            )
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=1)

    async def disconnect(self) -> None:
        """Закрывает соединение с RabbitMQ."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            self._channel = None
            self._queues = {}

    async def _ensure_connection(self) -> AbstractChannel:
        if self._channel is None:
            await self.connect()
            if self._channel is None:
                msg = 'Failed to establish RabbitMQ connection'
                raise RuntimeError(msg)
        return self._channel

    async def _create_message_processor(
        self,
        event_type: type[Any],
        event_name: str,
    ) -> typing.Coroutine:
        async def process_message(message: AbstractIncomingMessage) -> None:
            async with message.process():
                event_data = json.loads(message.body.decode())
                event_data = deserialize_datetime(event_data)
                event = event_type(**event_data)

                await gather(
                    *[handle_event_safely(sub.handler, event) for sub in self._subscriptions[event_name]],
                )

        return process_message

    async def subscribe(self, event_type: type[Any], handler: EventHandler) -> None:
        """Подписывает обработчик на событие и управляет потреблением из очереди."""
        channel = await self._ensure_connection()

        event_name = event_type.__name__
        if event_name not in self._subscriptions:
            self._subscriptions[event_name] = []

        # Если это первая подписка, настраиваем обменник, очередь и начинаем потребление
        if not self._subscriptions[event_name]:
            exchange_name = f'{event_name}_exchange'
            queue_name = f'{event_name}_queue'

            exchange = await channel.declare_exchange(
                exchange_name,
                ExchangeType.FANOUT,
                durable=True,
            )
            queue = await channel.declare_queue(queue_name, durable=True)
            await queue.bind(exchange)
            self._queues[event_name] = queue

            process_message = await self._create_message_processor(
                event_type,
                event_name,
            )
            consumer_tag = await queue.consume(process_message)
            self._consumer_tags[event_name] = consumer_tag

        self._subscriptions[event_name].append(EventSubscription(event_type, handler))

    async def unsubscribe(self, event_type: type[Any], handler: EventHandler) -> None:
        """Отписывает обработчик от события и останавливает потребление, если подписчиков больше нет."""
        event_name = event_type.__name__
        if event_name not in self._subscriptions:
            return
        self._subscriptions[event_name] = [
            sub for sub in self._subscriptions[event_name] if sub.handler != handler
        ]
        if not self._subscriptions[event_name] and event_name in self._consumer_tags:
            consumer_tag = self._consumer_tags.pop(event_name)
            if event_name in self._queues:
                queue = self._queues[event_name]
                await queue.cancel(consumer_tag)
                del self._queues[event_name]

    async def _serialize_event(self, event: Any) -> bytes:
        try:
            return json.dumps(event.__dict__, default=serialize_datetime).encode()
        except (AttributeError, TypeError) as e:
            event_name = event.__class__.__name__
            logger.exception(
                'Event serialization failed',
                **log_extra(
                    event_type=event_name,
                    event=str(event),
                    error=str(e),
                    error_type=e.__class__.__name__,
                ),
            )
            raise

    async def publish(self, event: Any) -> None:
        """Публикует событие в RabbitMQ."""
        if not self._active:
            return
        channel = await self._ensure_connection()

        event_name = event.__class__.__name__
        exchange_name = f'{event_name}_exchange'
        exchange = await channel.declare_exchange(
            exchange_name,
            ExchangeType.FANOUT,
            durable=True,
        )

        message_body = await self._serialize_event(event)
        message = aio_pika.Message(
            body=message_body,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key='')

    @asynccontextmanager
    async def pause(self) -> None:
        """Контекстный менеджер для временной приостановки публикации событий."""
        prev_state = self._active
        self._active = False
        try:
            yield
        finally:
            self._active = prev_state


def create_event_bus(settings: Settings) -> EventBus:
    """Фабричная функция для создания подходящей шины событий на основе настроек."""
    if settings.rabbitmq.use:
        return RabbitMQEventBus(settings)
    return InMemoryEventBus(settings.bus_exceptions)
