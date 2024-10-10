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
