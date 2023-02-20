from datetime import datetime
import json
import re
from typing import Any, Dict, List, Optional, Type
from uuid import UUID


def dict_has_any_keys(d: Dict, /, *, keys: List) -> bool:
    return any((key in keys for key in d))


def dict_has_all_keys(d: Dict, /, *, keys: List) -> bool:
    return all((key in keys for key in d))


def is_iterable(obj: Any, /) -> bool:
    return hasattr(obj, "__iter__")


def is_list_of_instances_of_type(obj: Any, /, *, type_: Type, allow_empty: Optional[bool] = True) -> bool:
    """Returns True if `obj` is a list of instances of type `type_`"""
    if not isinstance(obj, list):
        return False
    if not allow_empty and not obj:
        return False
    return all((isinstance(item, type_) for item in obj))


def is_valid_object_of_type(obj: Any, /, *, type_: Type, allow_empty: Optional[bool] = True) -> bool:
    if not isinstance(obj, type_):
        return False
    return True if allow_empty else bool(obj)


def is_valid_uuid_string(string: str, /) -> bool:
    if len(string) != 36:
        return False
    try:
        _ = UUID(string)
        return True
    except Exception:
        return False


def is_valid_datetime_string(string: str, format_: str, /) -> bool:
    """Returns True if given date/datetime string is valid; otherwise returns False"""
    try:
        _ = datetime.strptime(string, format_)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_json_string(string: str, /) -> bool:
    try:
        _ = json.loads(string)
        return True
    except (json.decoder.JSONDecodeError, TypeError):
        return False


def is_valid_email_id(email_id: str, /) -> bool:
    match_obj = re.fullmatch(
        pattern=re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'),
        string=email_id,
    )
    return True if match_obj else False


class _Empty:
    """Class used to denote an empty/missing value"""
    def __str__(self) -> str:
        return self.__class__.__name__


def set_as_empty() -> _Empty:
    return _Empty()


def is_empty(obj: Any, /) -> bool:
    return isinstance(obj, _Empty)


def is_instance_of_any(obj: Any, types: List[Type]) -> bool:
    return any((isinstance(obj, type_) for type_ in types))


def wrap_in_quotes_if_string(obj: Any, /) -> str:
    if isinstance(obj, str):
        return f"'{obj}'"
    return f"{obj}"