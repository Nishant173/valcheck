import copy
from datetime import date, datetime, timedelta, timezone
import json
import re
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from uuid import UUID


class Empty:
    """Class used to denote an empty/missing value"""
    def __str__(self) -> str:
        return f"<{self.__class__.__name__}>"


def set_as_empty() -> Empty:
    return Empty()


def is_empty(obj: Any, /) -> bool:
    return isinstance(obj, Empty)


def make_deep_copy(obj: Any, /) -> Any:
    """Returns a deep-copy of the given object"""
    return copy.deepcopy(obj)


def dict_has_any_keys(d: Dict, /, *, keys: List) -> bool:
    return any((key in keys for key in d))


def dict_has_all_keys(d: Dict, /, *, keys: List) -> bool:
    return all((key in keys for key in d))


def dicts_have_common_keys(d1: dict, d2: dict, /) -> bool:
    common_keys = set(d1.keys()).intersection(set(d2.keys()))
    return bool(common_keys)


def access_nested_dictionary(dict_: dict, /, *, path: List, default: Union[Any, Empty] = set_as_empty()) -> Any:
    """
    Returns the value accessed via `path` from the `dict_`.

    If `default` is not passed, raises:
        - `KeyError` if the `path` is not found.
        - `ValueError` if you try to access a nested list or tuple without an index (int) in the `path`.
        - `IndexError` if you try to access a nested list or tuple via an index, but the index is out of range.
    """
    assert isinstance(dict_, dict), "Param `dict_` must be a dictionary"
    assert isinstance(path, list) and bool(path), "Param `path` must be a non-empty list"
    result = dict_
    empty = set_as_empty()
    default_exists = not is_empty(default)
    path_traversed = []
    for item in path:
        path_traversed.append(item)

        if isinstance(result, dict):
            result = result.get(item, empty)
        elif isinstance(result, (list, tuple)):
            if not isinstance(item, int):
                if default_exists:
                    return default
                raise ValueError(
                    f"An index (int) is needed to access an item inside type '{result.__class__.__name__}' at path: {path_traversed[:-1]}"
                )
            try:
                result = result[item]
            except IndexError:
                if default_exists:
                    return default
                raise IndexError(f"Index `{item}` not found at path: {path_traversed}")
        else:
            if default_exists:
                return default
            raise ValueError(
                f"Cannot access path part `{item}` from item of type '{result.__class__.__name__}' at path: {path_traversed[:-1]}"
            )

        if is_empty(result):
            if default_exists:
                return default
            raise KeyError(f"Key not found at path: {path_traversed}")
    return result


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


def wrap_in_quotes_if_string(obj: Any, /) -> Any:
    if isinstance(obj, str):
        return f"'{obj}'"
    return obj


def is_collection_of_items(obj: Any, /) -> bool:
    """If the given `obj` is one of `[list, tuple, set]`, returns `True`"""
    return isinstance(obj, (list, tuple, set))


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


def is_empty_value_allowed(obj: Any, /, *, allow_empty: Optional[bool] = True) -> bool:
    return True if allow_empty else bool(obj)


def integerify_if_possible(value: Union[int, float], /) -> Union[int, float]:
    value_as_int = int(value)
    return value_as_int if value == value_as_int else value


def validate_number_string(value: Any, /) -> Tuple[Union[int, float, None], bool]:
    """
    Attempts to validate the given number string.
    Returns tuple of `(number_as_int_or_float, is_valid)`.
    If the number string is not valid, always returns `(None, False)`.
    """
    if not isinstance(value, str):
        return (None, False)
    try:
        number = float(value)
        if "." not in value:
            number = int(number)
    except Exception:
        return (None, False)
    return (number, True)


def is_valid_number_string(value: Any, /) -> bool:
    _, is_valid = validate_number_string(value)
    return is_valid


def validate_integer_string(value: Any, /) -> Tuple[Union[int, None], bool]:
    """
    Attempts to validate the given integer string.
    Returns tuple of `(number_as_int, is_valid)`.
    If the integer string is not valid, always returns `(None, False)`.
    """
    number, is_valid = validate_number_string(value)
    if is_valid and isinstance(number, int):
        return (number, True)
    return (None, False)


def is_valid_integer_string(value: Any, /) -> bool:
    _, is_valid = validate_integer_string(value)
    return is_valid


def validate_float_string(value: Any, /) -> Tuple[Union[float, None], bool]:
    """
    Attempts to validate the given float string.
    Returns tuple of `(number_as_float, is_valid)`.
    If the float string is not valid, always returns `(None, False)`.
    """
    number, is_valid = validate_number_string(value)
    if is_valid and isinstance(number, float):
        return (number, True)
    return (None, False)


def is_valid_float_string(value: Any, /) -> bool:
    _, is_valid = validate_float_string(value)
    return is_valid


def validate_uuid_string(value: Any, /) -> Tuple[Union[UUID, None], bool]:
    """
    Attempts to validate the given UUID string.
    Returns tuple of `(uuid_obj, is_valid)`.
    If the UUID string is not valid, always returns `(None, False)`.
    """
    if not isinstance(value, str):
        return (None, False)
    if len(value) != 36:
        return (None, False)
    try:
        uuid_obj = UUID(value)
    except Exception:
        return (None, False)
    return (uuid_obj, True)


def is_valid_uuid_string(value: Any, /) -> bool:
    _, is_valid = validate_uuid_string(value)
    return is_valid


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


def validate_date_string(value: Any, format_: str, /) -> Tuple[Union[date, None], bool]:
    """
    Attempts to validate the given date string.
    Returns tuple of `(date_obj, is_valid)`.
    If the date string is not valid, always returns `(None, False)`.
    """
    if not isinstance(value, str):
        return (None, False)
    try:
        date_obj = datetime.strptime(value, format_).date()
        is_valid = date_obj.strftime(format_) == value
    except Exception:
        return (None, False)
    else:
        return (date_obj, True) if is_valid else (None, False)


def is_valid_date_string(value: Any, format_: str, /) -> bool:
    """Returns True if given date string is valid; otherwise returns False"""
    _, is_valid = validate_date_string(value, format_)
    return is_valid


class TimezoneString:
    """Class that represents a timezone-string"""

    def __init__(self, tz_name: str, /) -> None:
        """
        Parameters:
            - tz_name (str): String that represents a timezone. Eg: `["UTC-02:30", "UTC", "UTC+05:30"]`.
        """
        assert isinstance(tz_name, str) and bool(tz_name), (
            "Param `tz_name` must be a non-empty string"
        )
        offset_string = self._compute_offset_string(tz_name)
        if offset_string is None:
            raise ValueError(f"Invalid '{self.__class__.__name__}' with value '{tz_name}'")

        self.tz_name: str = tz_name
        self.offset_string: str = offset_string

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(tz_name='{self.tz_name}')"

    def _compute_offset_string(self, tz_name: str, /) -> Union[str, None]:
        """
        If the given `tz_name` is valid, computes and returns the offset; otherwise returns `None`.
        Example offsets: `["-02:30", "+00:00", "+05:30"]`.
        """
        if not tz_name.startswith("UTC"):
            return None
        if tz_name == "UTC":
            return "+00:00"
        parts = tz_name.split("UTC")
        if not (
            len(parts) == 2
            and parts[0] == ""
            and len(parts[1]) == 6
        ):
            return None
        offset_string = parts[1]
        is_valid = (
            offset_string[0] in ("+", "-")
            and offset_string[1].isdigit()
            and offset_string[2].isdigit()
            and offset_string[3] == ":"
            and offset_string[4].isdigit()
            and offset_string[5].isdigit()
        )
        return offset_string if is_valid else None

    def as_timedelta(self) -> timedelta:
        """Returns the corresponding timedelta representation"""
        is_negative = self.offset_string[0] == "-"
        hours = int(f"{self.offset_string[1]}{self.offset_string[2]}")
        minutes = int(f"{self.offset_string[4]}{self.offset_string[5]}")
        timedelta_obj = timedelta(hours=hours, minutes=minutes)
        return -timedelta_obj if is_negative else timedelta_obj


def is_timezone_aware(dt_obj: datetime, /) -> bool:
    """Checks if the given datetime object is timezone-aware"""
    return dt_obj.tzinfo is not None


def get_tzname(dt_obj: datetime, /) -> Union[str, None]:
    """
    Returns the timezone name of the given datetime object.
    If the given datetime object is timezone-naive, returns `None`.
    """
    return dt_obj.tzinfo.tzname(dt_obj) if is_timezone_aware(dt_obj) else None


def is_datetime_of_timezone(dt_obj: datetime, /, *, allowed_tz_names: List[str]) -> bool:
    """
    Checks if the given datetime object belongs to one of the allowed timezones.

    Parameters:
        - dt_obj (datetime): Timezone-aware datetime object.
        - allowed_tz_names (List[str]): List of allowed timezone names.
    """
    assert is_timezone_aware(dt_obj), "Param `dt_obj` must be timezone-aware"
    assert isinstance(allowed_tz_names, list) and bool(allowed_tz_names), "Param `allowed_tz_names` must be a non-empty list"
    tz_name: str = get_tzname(dt_obj)
    return tz_name in allowed_tz_names


def convert_datetime_timezone(dt_obj: datetime, /, *, tz_name: str) -> datetime:
    """
    Converts the given datetime object to the specified timezome (`tz_name`).
    Expects timezone-aware datetime object.
    """
    assert is_timezone_aware(dt_obj), "Param `dt_obj` must be timezone-aware"
    offset = TimezoneString(tz_name).as_timedelta()
    tz = timezone(offset=offset)
    return dt_obj.astimezone(tz=tz)


def validate_datetime_string(
        value: Any,
        format_: str,
        /,
        *,
        allowed_tz_names: Optional[List[str]] = None,
        raise_if_tz_uncomparable: Optional[bool] = False,
    ) -> Tuple[Union[datetime, None], bool]:
    """
    Attempts to validate the given datetime string.
    Returns tuple of `(datetime_obj, is_valid)`.
    If the datetime string is not valid, always returns `(None, False)`.

    Parameters:
        - raise_if_tz_uncomparable (bool): If set to `True`, raises `ValueError` if the given datetime string is timezone-naive and
        the param `allowed_tz_names` is passed in, since we cannot check if a timezone-naive datetime string belongs to a particular timezone.
    """
    if not isinstance(value, str):
        return (None, False)
    try:
        datetime_obj = datetime.strptime(value, format_)
    except Exception:
        return (None, False)
    if allowed_tz_names:
        if not is_timezone_aware(datetime_obj):
            if raise_if_tz_uncomparable:
                raise ValueError(
                    "The given datetime string does not include a timezone."
                    f" Cannot check if a timezone-naive datetime string belongs to a particular timezone [{' | '.join(allowed_tz_names)}]."
                    " Suggest using a timezone-aware datetime string."
                )
            return (None, False)
        if not is_datetime_of_timezone(datetime_obj, allowed_tz_names=allowed_tz_names):
            return (None, False)
        return (datetime_obj, True)
    return (datetime_obj, True)


def is_valid_datetime_string(
        value: Any,
        format_: str,
        /,
        *,
        allowed_tz_names: Optional[List[str]] = None,
        raise_if_tz_uncomparable: Optional[bool] = False,
    ) -> bool:
    """Returns True if given datetime string is valid; otherwise returns False"""
    _, is_valid = validate_datetime_string(
        value,
        format_,
        allowed_tz_names=allowed_tz_names,
        raise_if_tz_uncomparable=raise_if_tz_uncomparable,
    )
    return is_valid


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


def validate_json_string(value: Any, /) -> Tuple[Union[Any, None], bool]:
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


def validate_json_object(value: Any, /) -> Tuple[Union[dict, None], bool]:
    parsed_obj, is_valid = validate_json_string(value)
    if is_valid and isinstance(parsed_obj, dict):
        return (parsed_obj, True)
    return (None, False)


def is_valid_json_object(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON object"""
    _, is_valid = validate_json_object(value)
    return is_valid


def validate_json_array(value: Any, /) -> Tuple[Union[list, None], bool]:
    parsed_obj, is_valid = validate_json_string(value)
    if is_valid and isinstance(parsed_obj, list):
        return (parsed_obj, True)
    return (None, False)


def is_valid_json_array(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON array"""
    _, is_valid = validate_json_array(value)
    return is_valid


def validate_json_object_or_array(value: Any, /) -> Tuple[Union[dict, list, None], bool]:
    parsed_obj, is_valid = validate_json_string(value)
    if is_valid and (isinstance(parsed_obj, dict) or isinstance(parsed_obj, list)):
        return (parsed_obj, True)
    return (None, False)


def is_valid_json_object_or_array(value: Any, /) -> bool:
    """Returns `True` if the given value is a string containing a valid JSON object or JSON array"""
    _, is_valid = validate_json_object_or_array(value)
    return is_valid


def is_valid_email_id_string(value: Any, /) -> bool:
    if not isinstance(value, str):
        return False
    match_obj = re.fullmatch(
        pattern=re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'),
        string=value,
    )
    return True if match_obj else False

