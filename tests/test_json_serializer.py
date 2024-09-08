from datetime import date, datetime
from typing import Any, Optional
import unittest
import uuid

from valcheck import utils
from valcheck.meta_classes import SingletonError
from valcheck.serializers.json_serializers import JsonSerializer, JsonSerializerSingleton


class Person:
    def __init__(self, *, name: str) -> None:
        assert isinstance(name, str) and bool(name), "Param `name` must be a non-empty string"
        self.name = name

    def greet(self) -> str:
        return f"<Class: {self.__class__.__name__}> || Hello from '{self.name}'"


class TestJsonSerializer(unittest.TestCase):

    def json_serializer_helper(self, obj: Any, /, *, print_details: Optional[bool] = False) -> None:
        """
        Expects a Python object that needs to be converted into a JSON string.

        Checks the functionality of the following:
            - `JsonSerializer.to_json_string()`
            - `JsonSerializer.from_json_string()`
        """
        json_serializer = JsonSerializer(include_default_serializers=True)
        json_serializer.register_serializers({
            Person: lambda value: value.greet(),
            date: lambda value: value.strftime("%d %B, %Y"),
            datetime: lambda value: value.strftime("%d %B, %Y || %I:%M:%S %p"),
        })
        json_string = json_serializer.to_json_string(obj)
        self.assertTrue(isinstance(json_string, str) and bool(json_string))
        python_obj = json_serializer.from_json_string(json_string)
        if utils.is_instance_of_any(obj, types=[dict, list]):
            self.assertTrue(
                utils.is_instance_of_any(python_obj, types=[dict, list])
            )
        if print_details:
            print(
                "\n\n\n\n\n",
                "START",
                f"Original object\n{obj}",
                f"JSON string\n{json_string}",
                f"Python object from JSON string\n{python_obj}",
                "END",
                sep="\n" + "=" * 100 + "\n",
            )

    def test_json_serializer(self):

        obj_01 = {
            "a": "Hello",
            "b": [1, 2, 3, 4.182192, None],
            "c": None,
            "d": utils.get_current_datetime(timezone_aware=True),
            "e": utils.get_current_date(timezone_aware=True),
            "f": uuid.uuid4(),
            "g": {
                "g1": None,
                "g2": {1, 2, 3},
                "g3": (4, 5, 6),
                "g4": set(list('abcdefgh')),
            },
            "h": {"1", "2", "3", "4", "5"},
            "i": (4, 5, 6),
            "j": Person(name="james"),
            "k": [
                '{"key1": "value1", "key2": "value2"}',
                utils.get_current_datetime(timezone_aware=True),
                utils.get_current_date(timezone_aware=True),
                uuid.uuid4(),
                {
                    "k1": None,
                    "k2": {1, 2, 3},
                    "k3": (4, 5, 6),
                    "k4": set(list('abcdefgh')),
                },
                Person(name="james murphy"),
                set([utils.get_current_datetime(timezone_aware=True), uuid.uuid4(), uuid.uuid4()]),
            ],
            "l": set([utils.get_current_datetime(timezone_aware=True), utils.get_current_date(timezone_aware=True), uuid.uuid4(), uuid.uuid1()]),
            "m": '{"key1": "value1", "key2": "value2"}',
        }
        self.json_serializer_helper(obj_01)

        obj_02 = set([
            1,
            2,
            2,
            3,
            3,
            4,
            uuid.uuid4(),
            Person(name="qwerty"),
            (
                "Hello",
                Person(name="asdf"),
                300,
                None,
                utils.get_current_date(timezone_aware=True),
                utils.get_current_datetime(timezone_aware=True),
            ),
        ])
        self.json_serializer_helper(obj_02)

        obj_03 = [
            1,
            2,
            2,
            3,
            3,
            4,
            uuid.uuid4(),
            Person(name="qwerty"),
            (
                "Hello",
                Person(name="asdf"),
                300,
                None,
            ),
            {
                "key1": uuid.uuid4(),
                "key2": utils.get_current_date(timezone_aware=True),
                "key3": utils.get_current_datetime(timezone_aware=True),
            },
            utils.get_current_date(timezone_aware=True),
            utils.get_current_datetime(timezone_aware=True),
        ]
        self.json_serializer_helper(obj_03)

        obj_04 = "hello"
        self.json_serializer_helper(obj_04)

        obj_05 = b"hello"
        self.json_serializer_helper(obj_05)

        obj_06 = utils.get_current_date(timezone_aware=True)
        self.json_serializer_helper(obj_06)

        obj_07 = utils.get_current_datetime(timezone_aware=True)
        self.json_serializer_helper(obj_07)

    def test_make_json_serializable(self):
        obj = {
            "aaa": datetime(year=2020, month=6, day=22, hour=17, minute=30, second=45),
            "bbb": date(year=2020, month=6, day=22),
            "ccc": uuid.UUID("09c35a0b-ed0b-486a-ab06-6f8de0e381fd"),
            "ddd": set([1, 2, 3, 3, 4, 4]),
        }
        expected_json_serializable = {
            "aaa": "2020-06-22 17:30:45",
            "bbb": "2020-06-22",
            "ccc": "09c35a0b-ed0b-486a-ab06-6f8de0e381fd",
            "ddd": [1, 2, 3, 4],
        }
        json_serializer = JsonSerializer(include_default_serializers=True)
        json_serializer.register_serializers({
            datetime: lambda value: value.strftime("%Y-%m-%d %H:%M:%S"),
        })
        obj_json_serializable = json_serializer.make_json_serializable(obj)
        self.assertTrue(id(obj) != id(obj_json_serializable))
        self.assertTrue(obj_json_serializable == expected_json_serializable)

    def test_json_serializer_singleton(self):
        json_serializer_singleton = JsonSerializerSingleton(include_default_serializers=True)
        self.assertTrue(isinstance(json_serializer_singleton, JsonSerializerSingleton))
        with self.assertRaises(SingletonError):
            JsonSerializerSingleton(include_default_serializers=True)

