import unittest

from valcheck import fields, validators


class ValidatorA(validators.Validator):
    a = fields.IntegerField()
    b = fields.IntegerField()
    c = fields.IntegerField()
    d = fields.IntegerField()


class TestValidator(unittest.TestCase):

    def test_deep_copy_in_validator(self):
        data = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
        }
        context = {"key": "value"}

        # case 1
        val = ValidatorA(data=data, context=context, deep_copy=False)
        self.assertTrue(
            val.data is data,
        )
        self.assertTrue(
            id(val.data) == id(data),
        )
        self.assertTrue(
            val.context is context,
        )
        self.assertTrue(
            id(val.context) == id(context),
        )

        # case 2
        val = ValidatorA(data=data, context=context, deep_copy=True)
        self.assertTrue(
            val.data is not data,
        )
        self.assertTrue(
            id(val.data) != id(data),
        )
        self.assertTrue(
            val.context is not context,
        )
        self.assertTrue(
            id(val.context) != id(context),
        )

    def test_validated_data_vs_extra_data(self):
        data = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5,
            "f": 6,
        }
        expected_validated_data = {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
        }
        expected_extra_data = {
            "e": 5,
            "f": 6,
        }
        val = ValidatorA(data=data)
        val.run_validations()
        errors = val.errors
        self.assertTrue(not errors)
        self.assertEqual(
            val.validated_data,
            expected_validated_data,
            msg="Param validated_data does not match",
        )
        self.assertEqual(
            val.extra_data,
            expected_extra_data,
            msg="Param extra_data does not match",
        )
