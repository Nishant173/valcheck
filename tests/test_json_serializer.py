from datetime import date, datetime
import unittest
import uuid

from valcheck import utils
from valcheck.json_utils import JsonSerializer, JsonSerializerSingleton
from valcheck.meta_classes import SingletonError


class Person:
    def __init__(self, *, name: str) -> None:
        assert isinstance(name, str) and bool(name), "Param `name` must be a non-empty string"
        self.name = name

    def greet(self) -> str:
        return f"<Class: {self.__class__.__name__}> || Hello from '{self.name}'"


class TestJsonSerializer(unittest.TestCase):

    def test_json_serializer(self):
        obj = {
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
        json_serializer = JsonSerializer(include_default_serializers=True)
        json_serializer.register_serializers({
            Person: lambda value: value.greet(),
            date: lambda value: value.strftime("%d %B, %Y"),
            datetime: lambda value: value.strftime("%d %B, %Y || %I:%M:%S %p"),
        })
        json_string = json_serializer.to_json_string(obj)
        self.assertTrue(isinstance(json_string, str) and bool(json_string))
        original_obj = json_serializer.from_json_string(json_string)
        self.assertTrue(isinstance(original_obj, dict) and bool(original_obj))

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

