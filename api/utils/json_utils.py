import json
from typing import Any, Optional

from utils.logger_init import logger


def to_json_string(
    value: Any,
    *,
    wrap_string_in_array: bool = False,
) -> Optional[str]:
    """
    Serialize dict/list values to JSON strings.

    - Returns None for None values.
    - Leaves plain strings as-is unless wrap_string_in_array=True, in which case
      invalid JSON strings will be wrapped into a JSON array.
    - Other primitive values (int, float, etc.) are returned unchanged.
    """
    if value is None:
        return None

    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value)
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to serialize value %s to JSON: %s", value, exc)
            return None

    if isinstance(value, str) and wrap_string_in_array:
        try:
            json.loads(value)
            return value
        except (json.JSONDecodeError, TypeError):
            try:
                return json.dumps([value])
            except (TypeError, ValueError) as exc:
                logger.warning("Failed to wrap string %s into JSON array: %s", value, exc)
                return None

    return value


def parse_json_field(value: Any, *, fallback: Any = None) -> Any:
    """
    Attempt to parse JSON strings into Python dict/list structures.
    Returns `fallback` when value is None, or the original value if parsing fails.
    """
    if value is None:
        return fallback

    if isinstance(value, (dict, list)):
        return value

    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError, ValueError):
            return value

    return value

