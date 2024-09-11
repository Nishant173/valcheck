import copy
from datetime import date, datetime, timezone
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from uuid import UUID


def get_current_datetime(*, timezone_aware: Optional[bool] = False) -> datetime:
    """
    Returns the current datetime (timezone-naive).
    If `timezone_aware=True`, returns a timezone-aware UTC datetime.
    """
    assert isinstance(timezone_aware, bool), "Param `timezone_aware` must be of type 'bool'"
    tz = timezone.utc if timezone_aware else None
    return datetime.now(tz=tz)


def get_current_date(*, timezone_aware: Optional[bool] = False) -> date:
    return get_current_datetime(timezone_aware=timezone_aware).date()


def make_deep_copy(obj: Any, /) -> Any:
    """Returns a deep-copy of the given object"""
    return copy.deepcopy(obj)


def dict_has_any_keys(d: Dict, /, *, keys: List) -> bool:
    return any((key in keys for key in d))


def dict_has_all_keys(d: Dict, /, *, keys: List) -> bool:
    return all((key in keys for key in d))


def make_message(
        message: str,
        /,
        *,
        prefix: Optional[str] = None,
        suffix: Optional[str] = None,
        sep: Optional[str] = None,
    ) -> str:
    sep = "" if sep is None else sep
    components = []
    if prefix:
        components.append(prefix)
    components.append(message)
    if suffix:
        components.append(suffix)
    return f"{sep}".join(components)


def is_list_of_instances_of_type(obj: Any, /, *, type_: Type, allow_empty: Optional[bool] = True) -> bool:
    """Returns True if `obj` is a list of instances of type `type_`"""
    if not isinstance(obj, list):
        return False
    if not allow_empty and not obj:
        return False
    return all((isinstance(item, type_) for item in obj))


def is_list_of_subclasses_of_type(obj: Any, /, *, type_: Type, allow_empty: Optional[bool] = True) -> bool:
    """Returns True if `obj` is a list of sub-classes of type `type_`"""
    if not isinstance(obj, list):
        return False
    if not allow_empty and not obj:
        return False
    return all((bool(isinstance(item, type) and issubclass(item, type_)) for item in obj))


def is_valid_object_of_type(obj: Any, /, *, type_: Type, allow_empty: Optional[bool] = True) -> bool:
    if not isinstance(obj, type_):
        return False
    return True if allow_empty else bool(obj)


def is_valid_uuid_string(value: Any, /) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) != 36:
        return False
    try:
        _ = UUID(value)
        return True
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def is_valid_date_string(value: Any, format_: str, /) -> bool:
    """Returns True if given date string is valid; otherwise returns False"""
    if not isinstance(value, str):
        return False
    try:
        return datetime.strptime(value, format_).date().strftime(format_) == value
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def is_valid_datetime_string(value: Any, format_: str, /) -> bool:
    """Returns True if given datetime string is valid; otherwise returns False"""
    if not isinstance(value, str):
        return False
    try:
        _ = datetime.strptime(value, format_)
        return True
    except (ValueError, TypeError):
        return False
    except Exception:
        return False


def from_json_string(value: Union[str, bytes, bytearray], /, **kwargs: Any) -> Any:
    """Converts JSON string into a Python object"""
    return json.loads(value, **kwargs)


def to_json_string(value: Any, /, **kwargs: Any) -> str:
    """Converts Python object into a JSON string"""
    if "indent" not in kwargs:
        kwargs["indent"] = 4
    if "sort_keys" not in kwargs:
        kwargs["sort_keys"] = True
    return json.dumps(value, **kwargs)


def validate_json_string(value: Any, /) -> Tuple[Any, bool]:
    """
    Attempts to parse the given JSON string.
    Returns tuple of `(parsed_obj, is_valid)`.
    If the JSON string is not valid, always returns `(None, False)`.
    """
    if not isinstance(value, str):
        return (None, False)
    try:
        parsed_obj = from_json_string(value)
    except Exception:
        return (None, False)
    return (parsed_obj, True)


def is_valid_json_string(value: Any, /) -> bool:
    _, is_valid = validate_json_string(value)
    return is_valid


def is_valid_json_object(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON object"""
    parsed_obj, is_valid = validate_json_string(value)
    return (
        is_valid
        and isinstance(parsed_obj, dict)
    )


def is_valid_json_array(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON array"""
    parsed_obj, is_valid = validate_json_string(value)
    return (
        is_valid
        and isinstance(parsed_obj, list)
    )


def is_valid_json_object_or_array(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON object or JSON array"""
    parsed_obj, is_valid = validate_json_string(value)
    return (
        is_valid
        and is_instance_of_any(parsed_obj, types=[dict, list])
    )


def is_valid_email_id_string(value: Any, /) -> bool:
    if not isinstance(value, str):
        return False
    match_obj = re.fullmatch(
        pattern=re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'),
        string=value,
    )
    return True if match_obj else False


def can_be_integer(value: Union[int, float], /) -> bool:
    return int(value) == value


def integerify_if_possible(value: Union[int, float], /) -> Union[int, float]:
    return int(value) if can_be_integer(value) else value


def is_valid_number_string(value: Any, /) -> bool:
    if not isinstance(value, str):
        return False
    try:
        _ = float(value)
        return True
    except (TypeError, ValueError):
        return False
    except Exception:
        return False


def is_valid_integer_string(value: Any, /) -> bool:
    return is_valid_number_string(value) and '.' not in value


def is_valid_float_string(value: Any, /) -> bool:
    return is_valid_number_string(value) and '.' in value


class Empty:
    """Class used to denote an empty/missing value"""
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


def set_as_empty() -> Empty:
    return Empty()


def is_empty(obj: Any, /) -> bool:
    return isinstance(obj, Empty)


def is_instance_of_any(obj: Any, types: List[Type]) -> bool:
    return any((isinstance(obj, type_) for type_ in types))


def is_collection_of_items(obj: Any, /) -> bool:
    """If the given `obj` is one of `[list, tuple, set]`, returns `True`"""
    return is_instance_of_any(obj, types=[list, tuple, set])


def wrap_in_quotes_if_string(obj: Any, /) -> Any:
    if isinstance(obj, str):
        return f"'{obj}'"
    return obj
