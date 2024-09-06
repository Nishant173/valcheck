from datetime import date, datetime
import json
from typing import Any, Callable, Dict, List, Type, Union
from uuid import UUID

from valcheck import utils

DictOrList = Union[Dict[str, Any], List[Any]]


class JsonSerializer:
    """Class that represents a JSON serializer."""

    def __init__(self) -> None:
        self._json_serializable_mapper: Dict[Type, Callable] = {
            bytes: lambda value: str(value),
            set: lambda value: list(value),
            str: lambda value: self.from_json_string(value) if utils.is_valid_json_string(value) else value,
            tuple: lambda value: list(value),
            date: lambda value: value.strftime("%Y-%m-%d"),
            datetime: lambda value: value.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            UUID: lambda value: str(value),
        }

    def register(
            self,
            *,
            type_: Type,
            func: Callable,
        ) -> None:
        """
        To register a serializer for a given type.
        Internally uses a type-to-callable mapping to convert a Python object to a JSON serializable value.

        Params:
            - type_: The type to serialize.
            - func: Callable that takes in the unserializable value as a param, and returns the serializable value.
        """
        assert isinstance(type_, type), "Param `type_` must be of type 'type'"
        assert callable(func), "Param `func` must be a callable"
        self._json_serializable_mapper.update({type_: func})

    def from_json_string(self, s: str, /, **kwargs: Any) -> DictOrList:
        """Converts JSON string into a Python dictionary/list"""
        assert isinstance(s, str), "Param `s` must be of type 'str'"
        s_copy = utils.make_deep_copy(s)
        return json.loads(s_copy, **kwargs)

    def to_json_string(self, obj: DictOrList, /, **kwargs: Any) -> str:
        """Converts Python dictionary/list into a JSON string"""
        assert utils.is_instance_of_any(obj, types=[dict, list]), "Param `obj` must be of type 'dict' or 'list'"
        obj_copy = utils.make_deep_copy(obj)
        obj_copy = self._make_json_serializable(obj_copy)
        if "indent" not in kwargs:
            kwargs["indent"] = 4
        if "sort_keys" not in kwargs:
            kwargs["sort_keys"] = True
        return json.dumps(obj_copy, **kwargs)

    def _make_json_serializable(self, obj: DictOrList, /) -> DictOrList:
        """Returns a dictionary/list which is JSON serializable. Modifies the given `obj` in-place."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    obj[key] = self._make_json_serializable(value)
                elif isinstance(value, list):
                    obj[key] = self._make_json_serializable(value)
                else:
                    func: Union[Callable, None] = self._json_serializable_mapper.get(type(value), None)
                    if func:
                        obj[key] = func(value)
                        if utils.is_instance_of_any(obj[key], types=[dict, list]):
                            obj[key] = self._make_json_serializable(obj[key])
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                if isinstance(item, dict):
                    obj[idx] = self._make_json_serializable(item)
                elif isinstance(item, list):
                    obj[idx] = self._make_json_serializable(item)
                else:
                    func: Union[Callable, None] = self._json_serializable_mapper.get(type(item), None)
                    if func:
                        obj[idx] = func(item)
                        if utils.is_instance_of_any(obj[idx], types=[dict, list]):
                            obj[idx] = self._make_json_serializable(obj[idx])
        return obj

