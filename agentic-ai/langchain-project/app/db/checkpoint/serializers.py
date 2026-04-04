import json
from datetime import datetime


def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def serialize_state(state: dict) -> str:
    return json.dumps(state, default=json_default, ensure_ascii=False)


def deserialize_state(state_json: str) -> dict:
    return json.loads(state_json)