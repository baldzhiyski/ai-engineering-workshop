import json
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


def to_jsonable(value):
    if isinstance(value, BaseModel):
        return value.model_dump()

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, date):
        return value.isoformat()

    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, UUID):
        return str(value)

    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}

    if isinstance(value, list):
        return [to_jsonable(item) for item in value]

    if isinstance(value, tuple):
        return [to_jsonable(item) for item in value]

    if isinstance(value, set):
        return [to_jsonable(item) for item in value]

    return value


def serialize_state(state: dict) -> str:
    safe_state = to_jsonable(state)
    return json.dumps(safe_state, ensure_ascii=False)


def deserialize_state(state_json: str) -> dict:
    return json.loads(state_json)