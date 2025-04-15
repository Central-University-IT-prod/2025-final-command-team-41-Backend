from datetime import UTC, datetime, timedelta, timezone

DEFAULT_TIMEZONE_OFFSET = timedelta(hours=3)  # UTC+3


def to_client_timezone(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(timezone(DEFAULT_TIMEZONE_OFFSET))


def to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
