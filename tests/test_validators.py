import unittest

from valcheck import fields, validators


class ValidatorA(validators.Validator):
    a = fields.IntegerField()
    b = fields.IntegerField()
    c = fields.IntegerField()
    d = fields.IntegerField()


class TestValidator(unittest.TestCase):

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
        errors = val.run_validations(raise_exception=False)
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

