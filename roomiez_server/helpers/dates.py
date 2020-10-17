from datetime import datetime, timezone


def utcnow():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def parse_iso(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc)


def to_iso(value):
    return value.astimezone(timezone.utc).isoformat()
