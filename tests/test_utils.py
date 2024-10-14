from datetime import datetime
import unittest

from valcheck import utils


class TestUtils(unittest.TestCase):

    def test_access_nested_dictionary(self):
        dictionary = {
            "full_name": "James Murphy",
            "favourite_hobby": {
                "hobby_id": "7e41ffc5-1106-4ad0-8aee-4a56c8d39ed6",
                "name": "hobby #1",
                "extra_v1": {
                    "key1": "value1",
                    "key2": "value2",
                    "key3": "value3",
                    "extra_v2": {
                        "key10": "value10",
                        "key20": "value20",
                        "key30": "value30",
                        "extra_v3": {
                            "key100": "value100",
                            "key200": "value200",
                            "key300": "value300",
                        },
                    },
                },
            },
            "other_hobbies_v1": [
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26613",
                    "name": "hobby #1",
                },
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26614",
                    "name": "hobby #2",
                },
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26615",
                    "name": "hobby #3",
                },
            ],
            "other_hobbies_v2": (
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26613",
                    "name": "hobby #1",
                },
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26614",
                    "name": "hobby #2",
                },
                {
                    "hobby_id": "9876dda8-c58d-43fd-8358-8c21a9a26615",
                    "name": "hobby #3",
                },
            ),
        }

        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["full_name"]),
            "James Murphy",
        )
        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["favourite_hobby", "name"]),
            "hobby #1",
        )
        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["favourite_hobby", "extra_v1", "extra_v2", "extra_v3", "key100"]),
            "value100",
        )
        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 0, "name"]),
            "hobby #1",
        )
        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 1, "name"]),
            "hobby #2",
        )
        self.assertEqual(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 2, "name"]),
            "hobby #3",
        )

        with self.assertRaises(KeyError):
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 2, "name-xxx"])
        with self.assertRaises(ValueError):
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", "2", "name"])
        with self.assertRaises(ValueError):
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 2, "name", "hello"])
        with self.assertRaises(IndexError):
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 300, "name"])

        self.assertIsNone(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 2, "name-xxx"], default=None),
        )
        self.assertIsNone(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", "2", "name"], default=None),
        )
        self.assertIsNone(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 2, "name", "hello"], default=None),
        )
        self.assertIsNone(
            utils.access_nested_dictionary(dictionary, path=["other_hobbies_v1", 300, "name"], default=None),
        )

    def test_timezone_string_class(self):
        timezone_string_1 = utils.TimezoneString("UTC-02:30")
        self.assertEqual(timezone_string_1.tz_name, "UTC-02:30")
        self.assertEqual(timezone_string_1.offset_string, "-02:30")

        timezone_string_2 = utils.TimezoneString("UTC")
        self.assertEqual(timezone_string_2.tz_name, "UTC")
        self.assertEqual(timezone_string_2.offset_string, "+00:00")

        timezone_string_3 = utils.TimezoneString("UTC+02:30")
        self.assertEqual(timezone_string_3.tz_name, "UTC+02:30")
        self.assertEqual(timezone_string_3.offset_string, "+02:30")

        with self.assertRaises(ValueError):
            utils.TimezoneString("-02:30")
        with self.assertRaises(ValueError):
            utils.TimezoneString("+00:00")
        with self.assertRaises(ValueError):
            utils.TimezoneString("+02:30")

    def test_is_datetime_of_timezone(self):
        datetime_string = "2020-04-20 17:30:45.585675+0530"
        format_ = "%Y-%m-%d %H:%M:%S.%f%z"

        dt_obj_tz_aware = datetime.strptime(datetime_string, format_)
        assert dt_obj_tz_aware.tzinfo is not None, "Ensure that `dt_obj_tz_aware` is timezone-aware in the test-case"
        dt_obj_tz_naive = dt_obj_tz_aware.replace(tzinfo=None)

        with self.assertRaises(AssertionError):
            utils.is_datetime_of_timezone(dt_obj_tz_naive, allowed_tz_names=["UTC", "UTC+05:30"])

        self.assertTrue(
            utils.is_datetime_of_timezone(dt_obj_tz_aware, allowed_tz_names=["UTC+05:30"]),
        )
        self.assertTrue(
            not utils.is_datetime_of_timezone(dt_obj_tz_aware, allowed_tz_names=["UTC"]),
        )

    def test_get_tzname(self):
        datetime_string = "2020-04-20 17:30:45.585675+0530"
        format_ = "%Y-%m-%d %H:%M:%S.%f%z"

        dt_obj_tz_aware = datetime.strptime(datetime_string, format_)
        assert dt_obj_tz_aware.tzinfo is not None, "Ensure that `dt_obj_tz_aware` is timezone-aware in the test-case"
        dt_obj_tz_naive = dt_obj_tz_aware.replace(tzinfo=None)

        self.assertEqual(
            utils.get_tzname(dt_obj_tz_aware),
            "UTC+05:30",
        )
        self.assertIsNone(
            utils.get_tzname(dt_obj_tz_naive),
        )

    def test_convert_datetime_timezone(self):
        datetime_string = "2020-04-20 17:30:45.585675+0000"
        format_ = "%Y-%m-%d %H:%M:%S.%f%z"

        dt_obj_tz_aware = datetime.strptime(datetime_string, format_)
        assert dt_obj_tz_aware.tzinfo is not None, "Ensure that `dt_obj_tz_aware` is timezone-aware in the test-case"

        self.assertEqual(
            utils.get_tzname(dt_obj_tz_aware),
            "UTC",
        )

        dt_obj_1 = utils.convert_datetime_timezone(dt_obj_tz_aware, tz_name="UTC+05:30")
        self.assertEqual(
            utils.get_tzname(dt_obj_1),
            "UTC+05:30",
        )

        dt_obj_2 = utils.convert_datetime_timezone(dt_obj_tz_aware, tz_name="UTC-02:30")
        self.assertEqual(
            utils.get_tzname(dt_obj_2),
            "UTC-02:30",
        )

        dt_obj_3 = utils.convert_datetime_timezone(dt_obj_tz_aware, tz_name="UTC+04:00")
        self.assertEqual(
            utils.get_tzname(dt_obj_3),
            "UTC+04:00",
        )

    def test_validate_datetime_string(self):
        string_tz_aware = "2020-04-20 17:30:45.585675+0000"
        format_tz_aware = "%Y-%m-%d %H:%M:%S.%f%z"

        string_tz_naive = "2020-04-20 17:30:45.585675"
        format_tz_naive = "%Y-%m-%d %H:%M:%S.%f"

        dt_obj_1, is_valid_1 = utils.validate_datetime_string(
            string_tz_aware,
            format_tz_aware,
            allowed_tz_names=["UTC"],
            raise_if_tz_uncomparable=False,
        )
        self.assertTrue(is_valid_1)
        self.assertTrue(utils.is_timezone_aware(dt_obj_1))

        dt_obj_2, is_valid_2 = utils.validate_datetime_string(
            string_tz_naive,
            format_tz_naive,
            allowed_tz_names=["UTC"],
            raise_if_tz_uncomparable=False,
        )
        self.assertFalse(is_valid_2)
        self.assertIsNone(dt_obj_2)

        with self.assertRaises(ValueError):
            utils.validate_datetime_string(
                string_tz_naive,
                format_tz_naive,
                allowed_tz_names=["UTC"],
                raise_if_tz_uncomparable=True,
            )

        dt_obj_3, is_valid_3 = utils.validate_datetime_string(
            string_tz_aware,
            format_tz_aware,
            allowed_tz_names=["UTC+05:30"],
            raise_if_tz_uncomparable=False,
        )
        self.assertFalse(is_valid_3)
        self.assertIsNone(dt_obj_3)

