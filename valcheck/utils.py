from datetime import datetime
import re
from typing import Any, Dict, List, Type
from uuid import UUID


def is_iterable(obj: Any, /) -> bool:
    return hasattr(obj, "__iter__")


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
    except ValueError:
        return False


def is_valid_email_id(email_id: str, /) -> bool:
    match_obj = re.fullmatch(
        pattern=re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'),
        string=email_id,
    )
    return True if match_obj else False


class _EmptyField:
    """Class used to denote an empty field (field whose value is missing)"""
    pass


def set_as_empty() -> _EmptyField:
    return _EmptyField()


def is_empty(obj: Any, /) -> bool:
    return isinstance(obj, _EmptyField)


def is_instance_of_any(obj: Any, types: List[Type]) -> bool:
    return any((isinstance(obj, type_) for type_ in types))


def is_key_present(dict_obj: Dict[str, Any], key: str) -> bool:
    return key in dict_obj


def get_class_variables_dict(class_: Type, /) -> Dict[str, Any]:
    return {
        key : value for key, value in vars(class_).items() if (
            not key.startswith("__")
            and key != 'Meta'
        )
    }